# language: pt
Funcionalidade: Autenticação de usuários
  Como visitante do Kapitour
  Quero me cadastrar e entrar na aplicação
  Para acessar conteúdo personalizado de Maricá

  Cenário: Cadastro com email disponível
    Dado que o email "novo@marica.gov.br" não está cadastrado
    Quando o usuário se registra com nome "Ana" e senha "segura123"
    Então o cadastro é concluído com sucesso
    E um token de acesso é emitido

  Cenário: Cadastro com email já existente
    Dado que o email "existente@marica.gov.br" já está cadastrado
    Quando o usuário tenta se registrar com o mesmo email
    Então o sistema rejeita o cadastro
    E informa que o email já está em uso

  Cenário: Login com credenciais válidas
    Dado que existe um usuário com email "turista@marica.gov.br" e senha "marica2024"
    Quando o usuário faz login com essas credenciais
    Então a autenticação é bem-sucedida
    E um token de acesso é emitido

  Cenário: Login com senha incorreta
    Dado que existe um usuário com email "turista@marica.gov.br" e senha "marica2024"
    Quando o usuário tenta login com senha "errada"
    Então a autenticação é recusada
