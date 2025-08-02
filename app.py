from flask import Flask, jsonify, request, abort
from flask_pydantic_spec import FlaskPydanticSpec, Response, Request
from pydantic import BaseModel
from tinydb import TinyDB


app = Flask(__name__)
spec = FlaskPydanticSpec('flask', title='Impulsiona Wyden')
spec.register(app)
database = TinyDB('database.json')
pessoas_table = database.table('pessoas')

class Pessoa(BaseModel):
   id: int
   name: str 
   idade: int
   altura: str

class Pessoas(BaseModel):
   pessoas: list[Pessoa]
   count: int
   
class PessoaOutput(BaseModel):
   mensagem: str


@app.post('/pessoas')
@spec.validate(body=Request(Pessoa), resp=Response(HTTP_200=Pessoa))
def inserir_pessoa():
   """Rota Responsavel por Inserir Pessoas"""
   dados = request.context.body.dict()
   pessoa_id = pessoas_table.insert(dados)
   dados['id'] = pessoa_id # Adiciona o ID à resposta
   return jsonify(dados)

@app.get('/pessoas')
@spec.validate(resp=Response(HTTP_200=Pessoas))
def buscar_pessoas():
  """Rota responsavel por Buscar Pessoas"""
  dados = pessoas_table.all()
  pessoas = [{'id': p.doc_id, **p} for p in dados]
  return jsonify(Pessoas(pessoas=pessoas, count=len(pessoas)).dict())

@app.get('/pessoas/<int:id>')
@spec.validate(resp=Response(HTTP_200=Pessoa))
def buscar_pessoa_por_id(id: int):
   """Busca pessoa por id"""
   pessoa = pessoas_table.get(doc_id=id)
   if not pessoa: 
      abort(404, description='Pessoa não encontrada')
   return jsonify(pessoa)

@app.delete('/pessoas/<int:id>')
@spec.validate(resp=Response(HTTP_200=PessoaOutput))
def deletar_pessoa(id: int):
   """Deletar pessoa por ID"""
   pessoa = pessoas_table.get(doc_id=id)
   if not pessoa:
      abort(404, description='Pessoa não encontrada')
   pessoas_table.remove(doc_ids=[id])
   return jsonify({'mensagem':f'Pessoa com ID {id} foi removida com sucesso.'})

@app.put('/pessoas/<int:id>')
@spec.validate(body=Request(Pessoa), resp=Response(HTTP_200=Pessoa))
def atualizar_pessoa(id: int):
   """Atualiza Pessoa por ID"""
   dados = request.context.body.dict()
   pessoa_existe = pessoas_table.get(doc_id=id)
   if not pessoa_existe:
      abort(404, description='Pessoa não encontrada')
   pessoas_table.update(dados, doc_ids=[id])
   dados['id'] = id
   return jsonify(dados)

if __name__=='__main__':
    app.run()
