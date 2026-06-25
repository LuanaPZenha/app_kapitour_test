# Sistema de QR Code e Cupons - Kapitour

## Visão Geral

Este sistema implementa um mecanismo de cupons baseado em QR Code para diferentes tipos de usuários no aplicativo Kapitour. O sistema permite que usuários parceiros escaneiem QR Codes de usuários comuns para resgatar cupons promocionais.

## Funcionalidades Implementadas

### 1. Sistema de QR Code

#### Para Usuários Comuns (tipo_usuario_id = 3) e Administradores (tipo_usuario_id = 1):
- **QR Code Pessoal**: Cada usuário possui um QR Code único contendo seu ID
- **Localização**: Área do Usuário → Botão "Ver QR Code"
- **Uso**: Apresentar para parceiros para resgatar cupons

#### Para Usuários Parceiros (tipo_usuario_id = 2):
- **Leitor de QR Code**: Botão para abrir o scanner
- **Localização**: Área do Usuário → Botão "Abrir Leitor"
- **Funcionalidade**: Escanear QR Codes dos usuários para resgatar cupons

### 2. Sistema de Cupons

#### Estrutura do Banco de Dados:
- **campanhas**: Promoções criadas pelos parceiros
- **cupons**: Cupons específicos com quantidade disponível e validade
- **cupons_resgatados**: Registro de todos os resgates realizados

#### Funcionalidades:
- **Cupons Disponíveis**: Parceiros veem seus cupons ativos
- **Histórico de Resgates**: Todos os usuários veem cupons já resgatados
- **Validação**: Sistema impede resgate duplicado do mesmo cupom
- **Controle de Quantidade**: Atualiza automaticamente a disponibilidade

## Arquivos Implementados

### 1. `Screens/AreaUsuario.jsx`
- **QR Code Container**: Exibido para usuários comuns e admins
- **Leitor Container**: Exibido para parceiros
- **Modal de Cupons**: Mostra cupons disponíveis e resgatados
- **Lógica Condicional**: Renderiza elementos baseado no tipo de usuário

### 2. `Screens/LeitorQR.jsx`
- **Interface do Scanner**: Interface para parceiros escanearem QR Codes
- **Modal de Resgate**: Seleção e resgate de cupons
- **Validações**: Verifica disponibilidade e duplicação

### 3. `utils/cupomManager.js`
- **Funções Utilitárias**: Centraliza toda a lógica de cupons
- **Validações**: Verifica disponibilidade, validade e duplicação
- **Operações CRUD**: Buscar, resgatar e gerenciar cupons

### 4. `App.js`
- **Navegação**: Adicionada rota para LeitorQR
- **Stack de Navegação**: Estrutura para telas adicionais

## Como Funciona

### Fluxo para Usuários Comuns/Admins:
1. Acessam a área do usuário
2. Veem seu QR Code pessoal
3. Apresentam o QR Code para parceiros
4. Visualizam histórico de cupons resgatados

### Fluxo para Parceiros:
1. Acessam a área do usuário
2. Clicam em "Abrir Leitor"
3. Escaneiam QR Code do usuário
4. Selecionam cupom para resgate
5. Sistema registra o resgate
6. Atualiza quantidade disponível

### Validações do Sistema:
- ✅ Verifica se o cupom ainda está disponível
- ✅ Verifica se a data de validade não expirou
- ✅ Impede resgate duplicado do mesmo cupom
- ✅ Atualiza automaticamente a quantidade disponível
- ✅ Registra data e hora do resgate

## Estrutura das Tabelas

### campanhas
```sql
- id (integer)
- nome (varchar)
- descricao (text)
- data_inicio (date)
- data_fim (date)
- ativa (boolean)
- criada_em (timestamp)
```

### cupons
```sql
- id (integer)
- codigo (varchar)
- descricao (text)
- criado_por (integer)
- parceiro_id (integer)
- data_validade (date)
- data_criacao (timestamp)
- quantidade_disponivel (integer)
- campanha_id (integer)
```

### cupons_resgatados
```sql
- id (integer)
- cupom_id (integer)
- usuario_id (integer)
- data_resgate (timestamp)
```

## Tecnologias Utilizadas

- **React Native**: Framework principal
- **react-native-qrcode-svg**: Geração de QR Codes
- **Supabase**: Backend e banco de dados
- **AsyncStorage**: Persistência local (se necessário)
- **React Navigation**: Navegação entre telas

## Configuração

### 1. Instalação de Dependências
```bash
npm install react-native-qrcode-svg
```

### 2. Configuração do Supabase
- Certifique-se de que as tabelas estão criadas no banco
- Configure as políticas de segurança adequadas
- Verifique as permissões de usuário

### 3. Tipos de Usuário
- **1**: Administrador (acesso completo + QR Code)
- **2**: Parceiro (leitor de QR + gerenciamento de cupons)
- **3**: Usuário Comum (QR Code + visualização de cupons)

## Testes

### Simulação de QR Code:
- Na tela do Leitor, use o botão "Simular Escaneamento"
- Sistema gera um ID aleatório para teste
- Permite testar o fluxo completo sem scanner real

### Cenários de Teste:
1. **Usuário Comum**: Verificar se QR Code é exibido
2. **Parceiro**: Verificar se leitor é exibido
3. **Resgate de Cupom**: Testar fluxo completo
4. **Validações**: Testar duplicação e disponibilidade

## Próximos Passos

### Melhorias Futuras:
- **Scanner Real**: Integrar com biblioteca de câmera
- **Notificações**: Alertas para cupons expirando
- **Relatórios**: Estatísticas de resgates
- **Push Notifications**: Alertas em tempo real
- **Geolocalização**: Cupons baseados em localização

### Funcionalidades Adicionais:
- **Cupons por Categoria**: Organização por tipo de promoção
- **Sistema de Pontos**: Acumular pontos por resgates
- **Cupons Personalizados**: Baseados no histórico do usuário
- **Integração com Pagamentos**: Cupons com valor monetário

## Suporte

Para dúvidas ou problemas:
1. Verificar logs do console
2. Validar estrutura do banco de dados
3. Confirmar permissões do Supabase
4. Verificar tipo de usuário no sistema

---

**Desenvolvido para o projeto Kapitour** 🚀
