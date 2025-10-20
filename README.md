### Projeto Medway

Aqui nesse repositório temos um projeto Django básico, já configurado para uso.

Para rodar o projeto, deve-se ter o docker e ligado instalado no computador.

Para configurár o projeto, pode-se rodar o comando:

`docker compose up --build`.

Isso deve inicializá-lo na porta 8000.

Ele já vai vir com alguns modelos, alguns inclusives já populados com dados de teste, 
para facilitar o desenvolvimento.

Com o projeto rodando, para acessar o container do docker, pode-se abrir outro terminal e rodar:

`docker exec -it medway-api bash`

Uma vez dentro do container, pode-se criar um usuário/estudante com o comando:

`python manage.py createsuperuser`

E utilizar essas credenciais para acessar o admin em http://0.0.0.0:8000/admin/.

## Testando os Endpoints da API

### 1. Enviar uma Prova (POST)

Primeiro, envie as respostas de um estudante para um exame:

```bash
curl -X POST http://localhost:8000/submissions/ \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "exam_id": 1,
    "answers": [
      {"question_id": 1, "alternative_id": 2},
      {"question_id": 2, "alternative_id": 5},
      {"question_id": 3, "alternative_id": 11}
    ]
  }'
```

**Response esperado (201 Created):**
```json
{
  "id": 1
}
```

### 2. Ver Resultado da Prova (GET)

Use o `id` retornado no passo anterior para buscar o resultado detalhado:

```bash
curl http://localhost:8000/submissions/1/
```

**Response esperado (200 OK):**
```json
{
  "id": 1,
  "student_id": 1,
  "student_name": "Admin",
  "exam_id": 2,
  "exam_name": "Prova Falsa 2",
  "submitted_at": "2025-10-19T23:55:35.309188Z",
  "score_data": {
    "total_questions": 3,
    "correct_answers": 0,
    "score": 0
  },
  "answers": [
    {
      "id": 1,
      "question_id": 1,
      "question_content": "Qual parte do corpo usamos para ouvir?",
      "selected_alternative_id": 2,
      "selected_alternative_content": "Cabelos",
      "selected_alternative_option": "B",
      "is_correct": false,
      "correct_alternative_id": 3,
      "correct_alternative_option": "C"
    },
    {
      "id": 2,
      "question_id": 2,
      "question_content": "Qual parte do corpo usamos para ver?",
      "selected_alternative_id": 7,
      "selected_alternative_content": "Mãos",
      "selected_alternative_option": "C",
      "is_correct": false,
      "correct_alternative_id": 6,
      "correct_alternative_option": "B"
    },
    {
      "id": 3,
      "question_id": 3,
      "question_content": "Qual parte do corpo usamos para cheirar?",
      "selected_alternative_id": 11,
      "selected_alternative_content": "Braços",
      "selected_alternative_option": "C",
      "is_correct": false,
      "correct_alternative_id": 9,
      "correct_alternative_option": "A"
    }
  ]
}
```

### 4. Possíveis Erros

#### Estudante já submeteu este exame (400)
```json
{
  "non_field_errors": [
    "This student has already submitted this exam"
  ]
}
```

#### Alternativa não pertence à questão (400)
```json
{
  "answers": [
    {
      "non_field_errors": [
        "Alternative 5 does not belong to question 1"
      ]
    }
  ]
}
```

#### Questão respondida mais de uma vez (400)
```json
{
  "answers": [
    "Not allowed to answer the same question more than once."
  ]
}
```