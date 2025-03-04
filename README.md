# 🏃‍♂️ Projeto +Saudável: Mexa-se e Some Pontos! 🚴‍♀️

Bem-vindo ao **Projeto +Saudável**! Nosso objetivo é estimular a prática de atividades físicas e uma alimentação equilibrada para melhorar a qualidade de vida dos participantes. Criamos um clube na plataforma **Strava**, onde você pode registrar suas atividades e competir de forma divertida com outros membros.

Aqui vale **TUDO**: correr, pedalar, caminhar, fazer yoga e até perseguir o cachorro que fugiu com sua meia (só cuidado com o pace)! A ideia é simples: **você se movimenta, junta pontos e a gente vibra com cada gota de suor.**

## 📊 Como Funciona o Clube de Pontos?

### 💪 Pontos Base

- Cada **1 minuto** de atividade registrada no Strava equivale a **1 ponto**.
- **Qualquer atividade física conta**, desde que seja registrada na plataforma.

### 🔥 Multiplicadores Semanais

Para incentivar a regularidade, aplicamos multiplicadores com base no número de dias ativos na semana:

| Dias Ativos na Semana | Multiplicador |
| --------------------- | ------------- |
| 1 dia ativo           | x1            |
| 2 dias ativos         | x1.2          |
| 3 dias ativos         | x1.3          |
| 4 dias ativos         | x1.4          |
| 5 a 7 dias ativos     | x1.5          |

> **Importante:** Se você fizer mais de uma atividade no mesmo dia, apenas um dia ativo será contabilizado para o multiplicador. No entanto, **todos os minutos das atividades do dia serão somados normalmente!**

### 🎉 Bônus por Eventos

Durante o ano, realizaremos **12 eventos especiais**. Ao participar de uma atividade em um desses dias, você ganha **+100 pontos fixos**, além da pontuação normal.

### 🏆 Exemplo de Pontuação Completa

Imagine que você treinou em 3 dias diferentes da semana e participou de um evento:

- **Segunda-feira:** 30 minutos de corrida + 20 minutos de yoga = **50 pontos** (1 dia ativo).
- **Quarta-feira:** 60 minutos de pedal = **60 pontos** (1 dia ativo).
- **Sexta-feira (evento especial):** 40 minutos de caminhada = **40 pontos + 100 pontos bônus = 140 pontos** (1 dia ativo).

**Cálculo final:**

- Total de pontos antes do multiplicador: **50 + 60 + 140 = 250 pontos**.
- Multiplicador por 3 dias ativos: **250 x 1.3 = 325 pontos**.
- **Pontuação final da semana: 325 pontos.**

Quanto mais dias ativos, **mais pontos e bônus você acumula!** 🚀

---

## 📡 Como Coletamos os Dados?

Para calcular a pontuação dos participantes, utilizamos **web scraping** na plataforma **Strava**. Como a API oficial possui restrições que limitam a coleta dos dados necessários para o ranking, optamos pelo scraping para acessar as informações **públicas** do clube.

---

## 🛠 Como Utilizar Este Projeto?

Antes de tudo, você precisa ter o **Python** instalado em sua máquina. Baixe a versão mais recente no site oficial:

🔗 [Download Python](https://www.python.org/downloads/)

### 🔹 Passo 1: Clonar o Repositório

```bash
git clone git@github.com:marcelohfonseca/prj-clube-mais-saudavel.git
```

### 🔹 Passo 2: Instalar Dependências

Utilize **pip** ou **uv** para instalar as dependências do projeto.

Instalar o **uv**:

```bash
pip install uv
```

Instalar dependências do projeto:

```bash
uv pip install
```

Se quiser instalar também as dependências de desenvolvimento:

```bash
uv pip install .[dev]
```

### 🔹 Passo 3: Executar o Projeto

Argumentos obrigatórios:
- **--club-id:** ID do clube no Strava.
- **--week:** Número de semanas a serem processadas.

Argumentos opcionais:
- **--score:** Calcula a pontuação de cada atleta.

```bash
python scrapper.py --club-id 12345 --week 2
```

> **Observação:** Certifique-se de configurar suas variáveis de ambiente corretamente antes de executar o script. Consulte o arquivo `.env.example` para mais detalhes.

---

## 🤝 Como Contribuir?

Quer ajudar a melhorar o projeto? Siga estes passos:

1. **Faça um fork do repositório**.
2. **Crie uma branch com sua funcionalidade:**

   ```bash
   git checkout -b feature/nome-da-sua-feature
   ```

3. **Realize suas alterações e faça um commit:**

   ```bash
   git commit -m 'feat: Adiciona nova funcionalidade X'
   ```

4. **Envie as alterações para seu repositório:**

   ```bash
   git push origin feature/nome-da-sua-feature
   ```

5. **Abra um Pull Request no repositório original.**

Antes de abrir um PR, verifique as **issues abertas** e, se necessário, crie uma nova para discutir sua ideia com a equipe.

---

🚀 Agora é com você! **Mexa-se e venha dominar o ranking!** 💪
