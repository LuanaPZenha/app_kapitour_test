# language: pt
Funcionalidade: Engajamento do turista
  Como usuário autenticado
  Quero favoritar pontos e avaliar experiências
  Para personalizar minha jornada

  Cenário: Listar favoritos com dados dos pontos
    Dado que o usuário possui pontos favoritados
    Quando solicito a lista de favoritos
    Então recebo cada favorito enriquecido com o ponto turístico

  Cenário: Calcular média de avaliações de um ponto
    Dado que um ponto possui duas avaliações
    Quando consulto a média do ponto
    Então o sistema retorna a média aritmética arredondada

  Cenário: Atualizar avaliação existente
    Dado que o usuário já avaliou um ponto
    Quando envia nova nota para o mesmo ponto
    Então a avaliação é atualizada em vez de duplicada
