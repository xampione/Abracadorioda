from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify, make_response, session
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from pdf_generator import generate_moliture_report
import json

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Pagina di login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        from models import User
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username, attivo=True).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            user.ultimo_accesso = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('index')
            return redirect(next_page)
        else:
            flash('Username o password non validi.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout dell'utente"""
    logout_user()
    flash('Logout effettuato con successo.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Dashboard principale"""
    from models import Cliente, Molitura
    
    # Statistiche rapide filtrate per sezioni accessibili
    accessible_sections = current_user.get_accessible_sections()
    totale_clienti = Cliente.query.count()
    moliture_in_corso = Molitura.query.filter(
        Molitura.stato.in_(['accettazione', 'in molitura']),
        Molitura.sezione.in_(accessible_sections)
    ).count()
    moliture_oggi = Molitura.query.filter(
        Molitura.data_ora >= datetime.now().date(),
        Molitura.sezione.in_(accessible_sections)
    ).count()
    
    # Ultime moliture filtrate per sezioni accessibili
    ultime_moliture = Molitura.query.filter(
        Molitura.sezione.in_(accessible_sections)
    ).order_by(Molitura.data_creazione.desc()).limit(5).all()
    
    return render_template('index.html', 
                         totale_clienti=totale_clienti,
                         moliture_in_corso=moliture_in_corso,
                         moliture_oggi=moliture_oggi,
                         ultime_moliture=ultime_moliture)

@app.route('/nuova_molitura', methods=['GET', 'POST'])
@login_required
def nuova_molitura():
    """Pagina per creare una nuova molitura"""
    from models import Cliente, Molitura, Cassone
    
    if request.method == 'POST':
        try:
            # Gestione cliente
            cliente_id = request.form.get('cliente_id')
            if not cliente_id:
                # Crea nuovo cliente
                cliente = Cliente(
                    nome=request.form['nome'],
                    cognome=request.form['cognome'],
                    telefono=request.form.get('telefono', ''),
                    indirizzo=request.form.get('indirizzo', ''),
                    email=request.form.get('email', ''),
                    note=request.form.get('note_cliente', '')
                )
                db.session.add(cliente)
                db.session.flush()  # Per ottenere l'ID
                cliente_id = cliente.id
            
            # Data e ora
            if request.form.get('usa_ora_corrente'):
                data_ora = datetime.now()
            else:
                data_str = request.form['data']
                ora_str = request.form['ora']
                data_ora = datetime.strptime(f"{data_str} {ora_str}", "%Y-%m-%d %H:%M")
            
            # Verifica permessi sezione
            sezione = int(request.form['sezione'])
            if not current_user.can_access_section(sezione):
                flash('Non hai i permessi per creare moliture in questa sezione.', 'error')
                return redirect(url_for('nuova_molitura'))
            
            # Crea molitura
            molitura = Molitura(
                cliente_id=cliente_id,
                sezione=sezione,
                data_ora=data_ora,
                stato=request.form['stato'],
                note=request.form.get('note_molitura', '')
            )
            db.session.add(molitura)
            db.session.flush()  # Per ottenere l'ID
            
            # Gestione cassoni
            cassoni_data = request.form.getlist('cassoni')
            for cassone_str in cassoni_data:
                if cassone_str:
                    numero, quantita = cassone_str.split(':')
                    cassone = Cassone(
                        molitura_id=molitura.id,
                        numero_cassone=int(numero),
                        quantita=int(quantita)
                    )
                    db.session.add(cassone)
            
            db.session.commit()
            flash('Molitura creata con successo!', 'success')
            return redirect(url_for('moliture'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore nella creazione della molitura: {str(e)}', 'error')
    
    clienti = Cliente.query.order_by(Cliente.cognome, Cliente.nome).all()
    return render_template('nuova_molitura.html', clienti=clienti)

@app.route('/moliture')
@login_required
def moliture():
    """Pagina lista moliture con filtri"""
    from models import Cliente, Molitura
    
    # Parametri di filtro
    data_da = request.args.get('data_da')
    data_a = request.args.get('data_a')
    stato = request.args.get('stato')
    sezione = request.args.get('sezione')
    
    # Query base filtrata per sezioni accessibili all'utente
    accessible_sections = current_user.get_accessible_sections()
    query = Molitura.query.join(Cliente).filter(Molitura.sezione.in_(accessible_sections))
    
    # Applicazione filtri
    if data_da:
        query = query.filter(Molitura.data_ora >= datetime.strptime(data_da, '%Y-%m-%d'))
    if data_a:
        query = query.filter(Molitura.data_ora <= datetime.strptime(data_a + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))
    if stato:
        query = query.filter(Molitura.stato == stato)
    if sezione:
        query = query.filter(Molitura.sezione == int(sezione))
    
    moliture = query.order_by(Molitura.data_ora.desc()).all()
    
    return render_template('moliture.html', moliture=moliture,
                         filtri={'data_da': data_da, 'data_a': data_a, 'stato': stato, 'sezione': sezione})

@app.route('/modifica_molitura/<int:id>', methods=['GET', 'POST'])
@login_required
def modifica_molitura(id):
    """Modifica una molitura esistente"""
    from models import Molitura, Cassone
    
    molitura = Molitura.query.get_or_404(id)
    
    # Verifica che l'utente possa accedere a questa sezione
    if not current_user.can_access_section(molitura.sezione):
        flash('Non hai i permessi per accedere a questa molitura.', 'error')
        return redirect(url_for('moliture'))
    
    if request.method == 'POST':
        try:
            # Aggiorna dati molitura
            molitura.sezione = int(request.form['sezione'])
            molitura.stato = request.form['stato']
            molitura.note = request.form.get('note_molitura', '')
            
            # Data e ora
            if request.form.get('usa_ora_corrente'):
                molitura.data_ora = datetime.now()
            else:
                data_str = request.form['data']
                ora_str = request.form['ora']
                molitura.data_ora = datetime.strptime(f"{data_str} {ora_str}", "%Y-%m-%d %H:%M")
            
            # Rimuovi cassoni esistenti
            Cassone.query.filter_by(molitura_id=id).delete()
            
            # Aggiungi nuovi cassoni
            cassoni_data = request.form.getlist('cassoni')
            for cassone_str in cassoni_data:
                if cassone_str:
                    numero, quantita = cassone_str.split(':')
                    cassone = Cassone(
                        molitura_id=molitura.id,
                        numero_cassone=int(numero),
                        quantita=int(quantita)
                    )
                    db.session.add(cassone)
            
            db.session.commit()
            flash('Molitura aggiornata con successo!', 'success')
            return redirect(url_for('moliture'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore nell\'aggiornamento della molitura: {str(e)}', 'error')
    
    # Converte i cassoni in formato dict per il template
    cassoni_data = [cassone.to_dict() for cassone in molitura.cassoni]
    return render_template('modifica_molitura.html', molitura=molitura, cassoni_data=cassoni_data)

@app.route('/elimina_molitura/<int:id>', methods=['POST'])
@login_required
def elimina_molitura(id):
    """Elimina una molitura"""
    from models import Molitura
    
    try:
        molitura = Molitura.query.get_or_404(id)
        db.session.delete(molitura)
        db.session.commit()
        flash('Molitura eliminata con successo!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore nell\'eliminazione della molitura: {str(e)}', 'error')
    
    return redirect(url_for('moliture'))

@app.route('/clienti')
@login_required
def clienti():
    """Pagina gestione clienti"""
    from models import Cliente
    
    clienti_list = Cliente.query.order_by(Cliente.cognome, Cliente.nome).all()
    clienti_data = [cliente.to_dict() for cliente in clienti_list]
    return render_template('clienti.html', clienti=clienti_list, clienti_data=clienti_data)

@app.route('/nuovo_cliente', methods=['POST'])
@login_required
def nuovo_cliente():
    """Crea un nuovo cliente"""
    from models import Cliente
    
    try:
        cliente = Cliente(
            nome=request.form['nome'],
            cognome=request.form['cognome'],
            telefono=request.form.get('telefono', ''),
            indirizzo=request.form.get('indirizzo', ''),
            email=request.form.get('email', ''),
            note=request.form.get('note', '')
        )
        db.session.add(cliente)
        db.session.commit()
        flash('Cliente creato con successo!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore nella creazione del cliente: {str(e)}', 'error')
    
    return redirect(url_for('clienti'))

@app.route('/modifica_cliente/<int:id>', methods=['POST'])
@login_required
def modifica_cliente(id):
    """Modifica un cliente esistente"""
    from models import Cliente
    
    try:
        cliente = Cliente.query.get_or_404(id)
        cliente.nome = request.form['nome']
        cliente.cognome = request.form['cognome']
        cliente.telefono = request.form.get('telefone', '')
        cliente.indirizzo = request.form.get('indirizzo', '')
        cliente.email = request.form.get('email', '')
        cliente.note = request.form.get('note', '')
        
        db.session.commit()
        flash('Cliente aggiornato con successo!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore nell\'aggiornamento del cliente: {str(e)}', 'error')
    
    return redirect(url_for('clienti'))

@app.route('/elimina_cliente/<int:id>', methods=['POST'])
@login_required
def elimina_cliente(id):
    """Elimina un cliente"""
    from models import Cliente
    
    try:
        cliente = Cliente.query.get_or_404(id)
        
        # Verifica se il cliente ha moliture associate
        if cliente.moliture:
            flash('Impossibile eliminare il cliente: ha moliture associate.', 'error')
        else:
            db.session.delete(cliente)
            db.session.commit()
            flash('Cliente eliminato con successo!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore nell\'eliminazione del cliente: {str(e)}', 'error')
    
    return redirect(url_for('clienti'))

@app.route('/search_clienti')
@login_required
def search_clienti():
    """API per ricerca clienti"""
    from models import Cliente
    
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify([])
    
    clienti = Cliente.query.filter(
        (Cliente.nome.ilike(f'%{query}%')) |
        (Cliente.cognome.ilike(f'%{query}%'))
    ).limit(10).all()
    
    return jsonify([cliente.to_dict() for cliente in clienti])

@app.route('/genera_report_pdf', methods=['POST'])
@login_required
def genera_report_pdf():
    """Genera report PDF per le moliture selezionate"""
    from models import Molitura
    
    try:
        moliture_ids = request.form.getlist('moliture_selezionate')
        if not moliture_ids:
            flash('Seleziona almeno una molitura per generare il report.', 'error')
            return redirect(url_for('moliture'))
        
        moliture = Molitura.query.filter(Molitura.id.in_(moliture_ids)).order_by(Molitura.data_ora).all()
        
        # Genera PDF
        pdf_buffer = generate_moliture_report(moliture)
        
        # Crea response
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=report_moliture_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        
        return response
        
    except Exception as e:
        flash(f'Errore nella generazione del report: {str(e)}', 'error')
        return redirect(url_for('moliture'))

@app.route('/cliente/<int:id>/moliture')
@login_required
def cliente_moliture(id):
    """Visualizza tutte le moliture di un cliente"""
    from models import Cliente, Molitura
    
    cliente = Cliente.query.get_or_404(id)
    
    # Filtra moliture per sezioni accessibili all'utente
    accessible_sections = current_user.get_accessible_sections()
    moliture = Molitura.query.filter_by(cliente_id=id).filter(
        Molitura.sezione.in_(accessible_sections)
    ).order_by(Molitura.data_ora.desc()).all()
    
    return render_template('cliente_moliture.html', cliente=cliente, moliture=moliture)

@app.route('/stampa_ricevuta/<int:id>')
@login_required
def stampa_ricevuta(id):
    """Genera ricevuta di stampa per stampante 58mm"""
    from models import Molitura
    
    molitura = Molitura.query.get_or_404(id)
    
    # Verifica che l'utente possa accedere a questa sezione
    if not current_user.can_access_section(molitura.sezione):
        flash('Non hai i permessi per accedere a questa molitura.', 'error')
        return redirect(url_for('moliture'))
    
    return render_template('ricevuta_58mm.html', molitura=molitura, datetime=datetime)
