# language: pt
Funcionalidade: Conteúdo turístico de Maricá
  Como visitante
  Quero consultar pontos e rotas
  Para planejar meu passeio

  Cenário: Listar todos os pontos turísticos
    Dado que existem pontos cadastrados no serviço de conteúdo
    Quando solicito a listagem de pontos
    Então recebo a lista completa de pontos

  Cenário: Buscar pontos por categoria
    Dado que existem pontos em categorias distintas
    Quando filtro pontos pela categoria "Praias"
    Então recebo apenas pontos dessa categoria

  Cenário: Obter pontos de uma rota
    Dado que existe a rota "Rota Litorânea" com pontos associados
    Quando consulto os pontos da rota
    Então recebo os pontos na ordem da rota
