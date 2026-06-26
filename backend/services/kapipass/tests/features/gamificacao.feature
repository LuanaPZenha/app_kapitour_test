# language: pt
Funcionalidade: Gamificação KapiPass
  Como turista explorando Maricá
  Quero progredir em missões e desbloquear conquistas
  Para me motivar a visitar mais pontos

  Cenário: Progresso de missão por pontos visitados
    Dado que a missão usa estratégia de pontos visitados
    Quando calculo o progresso com 4 visitas
    Então o progresso registrado é 4

  Cenário: Progresso de missão por carimbos
    Dado que a missão usa estratégia de carimbos
    Quando calculo o progresso com 7 carimbos
    Então o progresso registrado é 7

  Cenário: Conquista explorador desbloqueada
    Dado que o turista visitou pelo menos 1 ponto
    Quando avalio a conquista "explorador_marica"
    Então o critério é atendido

  Cenário: Conquista de carimbos ainda bloqueada
    Dado que o turista possui apenas 2 carimbos
    Quando avalio a conquista "colecionador_carimbos"
    Então o critério não é atendido
