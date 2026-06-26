# language: pt
Funcionalidade: Perfil de usuário
  Como usuário autenticado
  Quero consultar e atualizar meu perfil
  Para manter meus dados corretos

  Cenário: Verificar email disponível
    Dado que o email "livre@marica.gov.br" não está cadastrado
    Quando verifico se o email existe
    Então o sistema informa que o email está disponível

  Cenário: Atualizar perfil com email de outro usuário
    Dado que existem dois usuários cadastrados
    Quando o primeiro tenta usar o email do segundo
    Então a atualização é rejeitada
