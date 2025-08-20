# Em @db_cli.command('reset')
@click.option('--with-seed/--no-seed', default=True, help="Popula o banco com dados demo após o reset.")
@with_appcontext
def reset_command(with_seed): # <-- note o novo parâmetro
    """
    [CUIDADO] Apaga todos os dados e recria o banco do zero.
    """
    # ... (código de confirmação) ...
    try:
        db.drop_all()
        click.secho("-> Todas as tabelas foram apagadas.", fg="yellow")

        init_command.main()
        if with_seed: # <-- a mágica acontece aqui
            seed_command.main()

        click.secho("\nBanco de dados resetado e inicializado com sucesso!", fg="green", bold=True)
    # ... (código de erro) ...