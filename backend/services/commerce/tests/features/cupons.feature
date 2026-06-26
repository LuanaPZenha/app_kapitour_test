# language: pt
Funcionalidade: Resgate de cupons
  Como turista
  Quero resgatar cupons de parceiros
  Para obter benefícios durante minha visita

  Cenário: Resgate de cupom disponível
    Dado que existe um cupom válido e não resgatado
    Quando o usuário resgata o cupom
    Então o resgate é confirmado com sucesso

  Cenário: Tentativa de resgatar cupom já utilizado
    Dado que o usuário já resgatou o cupom
    Quando tenta resgatar novamente
    Então o sistema impede o resgate duplicado

  Cenário: Cupom expirado
    Dado que o cupom está com data de validade vencida
    Quando o usuário tenta resgatar
    Então o sistema informa que o cupom expirou

  Cenário: Cupom de outro parceiro
    Dado que o cupom pertence a um parceiro diferente
    Quando o usuário tenta resgatar na loja errada
    Então o sistema rejeita por parceiro incorreto
