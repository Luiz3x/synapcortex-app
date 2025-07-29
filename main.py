# Substitua a função inteira no main.py

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        email = request.form.get('email').lower()
        password = request.form.get('password')
        cnpj = request.form.get('cnpj')
        nome_empresa = request.form.get('nome_empresa', '')
        
        # >>> INÍCIO DA NOVA VALIDAÇÃO <<<
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Verifica se o CNPJ é numérico e tem 14 dígitos
        if not cnpj or not cnpj.isdigit() or len(cnpj) != 14:
            message = 'CNPJ inválido. Por favor, insira 14 números.'
            if is_ajax:
                return jsonify({'success': False, 'message': message}), 400 # 400 = Bad Request
            return render_template('registrar.html', error=message)
        # >>> FIM DA NOVA VALIDAÇÃO <<<

        usuarios = carregar_json(CAMINHO_USUARIOS)

        if email in usuarios:
            message = 'Este e-mail já está cadastrado.'
            if is_ajax:
                return jsonify({'success': False, 'message': message}), 409
            return render_template('registrar.html', error=message)
        
        for user_data in usuarios.values():
            if user_data.get('cnpj') == cnpj:
                message = 'Este CNPJ já possui um cadastro.'
                if is_ajax:
                    return jsonify({'success': False, 'message': message}), 409
                return render_template('registrar.html', error=message)

        hashed_password = generate_password_hash(password)
        data_inicio = datetime.now()
        data_fim = data_inicio + timedelta(days=30)
        
        usuarios[email] = {
            'senha': hashed_password, 'cnpj': cnpj, 'nome_empresa': nome_empresa,
            'status_assinatura': 'ativo',
            'data_inicio_assinatura': data_inicio.strftime('%Y-%m-%d'), # Corrigido
            'data_fim_assinatura': data_fim.strftime('%Y-%m-%d'), # Corrigido
            'configuracoes': {
                'popup_titulo': 'Não vá embora!',
                'popup_mensagem': 'Temos uma oferta especial para você.',
                'tatica_mobile': 'foco',
                'ativar_quarto_bem_vindo': False,
                'ativar_quarto_interessado': False
            }
        }
        salvar_json(CAMINHO_USUARIOS, usuarios)

        if is_ajax:
            return jsonify({'success': True, 'redirect_url': url_for('login', message='Cadastro realizado com sucesso!')})
        return redirect(url_for('login', message='Cadastro realizado com sucesso!'))

    return render_template('registrar.html')