// cartas.js - As 10 cartas do Sussurro do Dia
const cartas = [
  {
    id: 1,
    nome: "Jurema",
    nomeCientifico: "Mimosa tenuiflora",
    mensagem: "Eu abro portais que o mundo fechou. Hoje é dia de olhar para dentro.",
    ritual: "Defumação rápida com casca ou folhas (2 min) + reza de proteção.",
    significado: "Entidade ancestral que pede reciprocidade.",
    cor: "#8B4513",
    tempoRitual: 2
  },
  {
    id: 2,
    nome: "Arruda",
    nomeCientifico: "Ruta graveolens",
    mensagem: "Guardiã dos quintais, eu quebro o que não te pertence.",
    ritual: "Passe um galho fresco pelo corpo com intenção de limpeza.",
    significado: "Proteção e descarrego.",
    cor: "#4CAF50",
    tempoRitual: 3
  },
  {
    id: 3,
    nome: "Alfavaca",
    nomeCientifico: "Ocimum gratissimum",
    mensagem: "Selvagem e intensa, eu limpo o pesado e abro o caminho da prosperidade.",
    ritual: "Banho matinal com folhas frescas.",
    significado: "Prosperidade e limpeza pesada.",
    cor: "#2E7D32",
    tempoRitual: 5
  },
  {
    id: 4,
    nome: "Cipó de Alho",
    nomeCientifico: "Mansoa alliacea",
    mensagem: "Eu levanto barreiras de luz onde a sombra tenta entrar.",
    ritual: "Defumação de folhas secas no ambiente.",
    significado: "Proteção espiritual.",
    cor: "#1B5E20",
    tempoRitual: 3
  },
  {
    id: 5,
    nome: "Breu Branco",
    nomeCientifico: "Protium heptaphyllum",
    mensagem: "Minha fumaça purifica o que o olho não vê.",
    ritual: "Queime em brasa e caminhe anti-horário pela casa.",
    significado: "Purificação profunda.",
    cor: "#D4A017",
    tempoRitual: 5
  },
  {
    id: 6,
    nome: "Pau-Rosa",
    nomeCientifico: "Aniba rosaeodora",
    mensagem: "Eu curo o que o coração carrega em silêncio.",
    ritual: "Óleo no pulso + meditação de 3 minutos.",
    significado: "Cura emocional.",
    cor: "#E91E63",
    tempoRitual: 3
  },
  {
    id: 7,
    nome: "Sal 3 em 1 - Limpeza Profunda",
    nomeCientifico: "Sal de ervas",
    mensagem: "Eu removo o que já não serve mais.",
    ritual: "Banho ou escalda-pés com o produto.",
    significado: "Limpeza energética.",
    cor: "#9E9E9E",
    tempoRitual: 10
  },
  {
    id: 8,
    nome: "Sal 3 em 1 - Proteção",
    nomeCientifico: "Sal de ervas",
    mensagem: "Eu guardo teus passos e abro as portas certas.",
    ritual: "Passe nos pés e mãos antes de sair.",
    significado: "Proteção nos caminhos.",
    cor: "#607D8B",
    tempoRitual: 3
  },
  {
    id: 9,
    nome: "Sal 3 em 1 - Prosperidade",
    nomeCientifico: "Sal de ervas",
    mensagem: "Eu ativo o fluxo que a floresta sempre soube dar.",
    ritual: "Coloque um pires com sal perto da entrada da casa.",
    significado: "Abertura de caminhos.",
    cor: "#FFC107",
    tempoRitual: 3
  },
  {
    id: 10,
    nome: "Lua Nova",
    nomeCientifico: "Ciclo Lunar",
    mensagem: "É tempo de plantar sementes invisíveis.",
    ritual: "Escreva 3 desejos em um papel e enterre em um vaso.",
    significado: "Novos começos.",
    cor: "#B0BEC5",
    tempoRitual: 5
  }
];

// Função para pegar a carta do dia (baseado na data)
function getCartaDoDia() {
  const hoje = new Date();
  const diaDoAno = Math.floor((hoje - new Date(hoje.getFullYear(), 0, 0)) / 86400000);
  const indice = diaDoAno % cartas.length;
  return cartas[indice];
}