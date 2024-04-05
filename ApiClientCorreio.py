
import base64
import requests
import json
import math
import data_defaults as data_c

class ApiClientCorreios:
    default_url = 'https://api.correios.com.br/'
    def __init__(self, user, acess_code, post_card, contract, token):
        self.url = ''
        self.user =user
        self.acess_code = acess_code
        self.post_card = post_card
        self.contract = contract
        self.token = token 
        

    def refresh_token(self, mode='cartao_postagem'):
        """
        Atualiza o token de autenticação para acesso a recursos específicos da API dos Correios.

        Args:
            mode (str): O modo de autenticação. Padrão é 'cartao_postagem'.
            - cartao_postagem :  Token para as APIs : 27,34,35,36,37,41,76,78,80,83,87,93,566,587
            - contrato : Token permite acessa  27,34,35,41,76,78,87,566,587
            - '' (vazio)
            

        Returns:
            dict: Um dicionário contendo informações sobre o token atualizado. 
                As chaves são 'token_refresh_date', 'token_expire_date' e 'token'.
                Retorna None em caso de erro.

        Raises:
            ValueError: Se o modo de autenticação não for reconhecido.
        """


        
        basic =bytes(f'{self.user}:{self.acess_code}', encoding='utf-8')
        basic = str(base64.b64encode(basic), encoding='utf-8')
        
            
        header = {'accept': 'application/json',
                    'Content-Type': 'application/json',
                    'Authorization': f'Basic {basic}'
                    }

        if(mode == 'cartao_postagem'):

            self.url = f'{self.default_url}token/v1/autentica/cartaopostagem'
            data = {'numero':self.post_card}
            respose = requests.post(url = self.url, json= data, headers= header)
            
            if respose.status_code == 201:
                respose_json = respose.json()
                self.token = respose_json['token']
                return {
                'token_refresh_date' :respose_json['emissao'],
                'token_expire_date' :respose_json['expiraEm'],
                'token': self.token
                }
            
            elif(respose.status_code == 400):
                print('Erro de validação verifique se todas informações foram passadas corretamente')

            elif(respose.status_code == 500):
                print('Erro no servidor , tente novamente mais tarde')
            else:
                print(respose.content)
            return None
        
        elif(mode == 'contrato'):

            self.url = f'{self.default_url}token/v1/autentica/contrato'
            data = {'numero':self.contract}
            
            respose = requests.post(url = self.url, json= data, headers= header)
            
            if respose.status_code == 201:
                respose_json = respose.json()
                self.token = respose_json['token']
                return {
                'token_refresh_date' :respose_json['emissao'],
                'token_expire_date' :respose_json['expiraEm'],
                'token': self.token
                }
            
            elif(respose.status_code == 400):
                print('Erro de validação verifique se todas informações foram passadas corretamente')

            elif(respose.status_code == 500):
                print('Erro no servidor , tente novamente mais tarde')
            else:
                print(respose.content)

        elif(mode == ''):
            
            self.url = f'{self.default_url}token/v1/autentica'
            
            respose = requests.post(url = self.url, json= '', headers= header)
            
            if respose.status_code == 201:
                respose_json = respose.json()
                self.token = respose_json['token']
                return {
                'token_refresh_date' :respose_json['emissao'],
                'token_expire_date' :respose_json['expiraEm'],
                'token': self.token
                }
            
            elif(respose.status_code == 400):
                print('Erro de validação verifique se todas informações foram passadas corretamente')

            elif(respose.status_code == 500):
                print('Erro no servidor , tente novamente mais tarde')
            else:
                print(respose.content)
        
        else:
            raise ValueError("Modo de autenticação não reconhecido.")
        
    def header(self):

        header = {'accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.token}'}


        return header 
        
    def tracking_package(self, query_type, *args):

        """
        Realiza o rastreamento de pacotes de acordo com o tipo de consulta especificado.

        Args:
            query_type (str): O tipo de consulta a ser realizada. Deve ser um dos seguintes valores:
            - 'U' para obter a última atualização do pacote.
            - 'T' para obter todas as atualizações do pacote.
            - 'P' para obter a primeira atualização do pacote.

            *args (list or tuple): Uma lista ou tupla contendo os códigos de rastreamento dos pacotes.

        Returns:
            list: Uma lista de dicionários contendo informações sobre o rastreamento de cada pacote. Cada dicionário possui as seguintes chaves:
            - 'codigo': O código de rastreamento do pacote.
            - 'dtPrevista': A data e hora previstas para a entrega do pacote.
            - 'dtEvent': Uma lista de datas e horas de eventos relacionados ao pacote.
            - 'description': Uma lista de descrições dos eventos ocorridos com o pacote.
            - 'local': Uma lista de locais onde ocorreram os eventos.
            - 'cidade': Uma lista de cidades associadas aos eventos.
            - 'uf': Uma lista de estados associados aos eventos.

        Raises:
            ValueError: Se nenhum código de rastreamento for fornecido.
            Exception: Se ocorrer um erro durante a solicitação de rastreamento.

        Exemplo:
            Para rastrear pacotes com códigos 'ABC123' e 'DEF456':

            >>> tracker = ApiClientCorreios(args)
            >>> result = tracker.tracking_package('U', 'AA000000000BR', 'AA000000001BR')
            >>> print(result)

            ou 

            >>> tracker = ApiClientCorreios(args)
            >>> result = tracker.tracking_package('U', ('AA000000000BR', 'AA000000001BR'))
            >>> print(result)
        """
        
        self.url = f'{self.default_url}srorastro/v1/objetos'
        limit = 50
    
        if len(args)==1 and isinstance(args[0],(list, tuple)):
            tracking_codes = args[0]
        else:
            tracking_codes = args
        
        n_request_needed = 1

        if len(tracking_codes) > limit:
            n_request_needed = math.ceil(len(tracking_codes)/limit)

        packages =[]
        
        for i in range(n_request_needed):

            
            params ={'codigosObjetos': tracking_codes[limit*i:limit*(i+1)],
                    'resultado': query_type}
            
            
            response = requests.get(self.url,params= params, headers= self.header() )
            if response.status_code == 200:
                response_json = response.json()
                
                packages.extend(response_json.get('objetos'))
            
            

            elif response.status_code == 400:
                print("Algo deu errado confira o Token")
            else:
                print("Caso ocorra algum erro no servidor. Tente novamente mais tarde")	

        tracking_list = []

        for package in packages:
            object ={
                    'codigo': package.get('codObjeto')
                    }

            if 'eventos' in package:
                object.update({'dtPrevista': package.get('dtPrevista')})
                dtEvent = []
                description = []
                place = []
                city = []
                uf = []

                for step in package.get('eventos'):
                    dtEvent.append(step.get('dtHrCriado'))
                    description.append(step.get('descricao'))
                    place.append(step.get('unidade').get('tipo'))
                    city.append(step.get('unidade').get('endereco').get('cidade'))
                    uf.append(step.get('unidade').get('endereco').get('uf'))

                object.update({
                    'dtEvent':dtEvent,
                    'description':description,
                    'local': place,
                    'cidade': city,
                    'uf': uf
                })
            else:
                object.update({description:package.get('mensagem')}) 

            tracking_list.append(object)  

        return tracking_list
                

    def delivery_forecast(self, types, *args):

        """
        Consulta a previsão de entrega para os tipos de produtos especificados.

        Args:
            types (list): Uma lista de códigos de produtos para os quais se deseja obter previsão de entrega
            (estes codigos podem serem encontrados ao fazer simulação so site dos correios empresas.correios... 
            ou atraves do manual do SIGEP).
            *args: Argumentos contendo informações sobre os locais de origem (CEP) e destino (CEP), 
                bem como a data de postagem e a data do evento (dia atual). A ordem dos argumentos é:
                cepOrigem, cepDestino, dataPostagem, dtEvento.

        Returns:
            dict or None: Um dicionário contendo as previsões de entrega para cada produto, 
                        conforme retornadas pela API dos Correios. Retorna None em caso de erro 
                        na solicitação.

        Raises:
            Exception: Se a solicitação para a API dos Correios falhar por qualquer motivo.

        Example:
            # Exemplo de uso:
            api = CorreiosAPI(api_key)
            forecast = api.delivery_forecast(['03220', '03298'], '01000-000', '04000-000', 
                                            '2024-04-04', '2024-04-05')
            if forecast:
                print("Previsão de entrega:")
                for item in forecast['parametrosPrazo']:
                    print(f"Produto: {item['coProduto']}")
                    print(f"Prazo de entrega: {item['prazoEntrega']} dias")
            else:
                print("Falha ao obter previsão de entrega.")
        """

        self.url = f'{self.default_url}prazo/v1/nacional'
        
        template = data_c.info_delivery_times
        param_prazos = []

        template["nuRequisicao"] = '1'
        template["dtEvento"] = args[3]
        template["cepOrigem"] = args[0]
        template["cepDestino"] = args[1]
        template["dataPostagem"]= args[2]
            
        for prod in types:
            template["coProduto"] = str(prod)
            param_prazos.append(template.copy())

        api_model_prazos = {
            "idLote": "1",
            "parametrosPrazo": param_prazos      
            }


        response = requests.post(self.url, json = api_model_prazos, headers= self.header() )
        if response.status_code == 200:
            response_json = response.json()
            return(response_json)
        else:
            print(response.text)
            return None
        
        

        


        




        
        



if __name__ == '__main__':
    from dotenv import dotenv_values

    config = dotenv_values(".env")
    
    user =config.get('USER')
    acess_token = config.get('ACESS_TOKEN')
    post_card = config.get('POST_CARD')
    contract = config.get('N_CONTRACT')
    token = config.get('token')
    correios =ApiClientCorreios(user, acess_token, post_card, contract,token)
    fresh_token1= correios.refresh_token()
    print(fresh_token1)

    a = correios.tracking_package('U','AA037090154BR', 'AV001914319BR')
    # 03220 - SEDEX CONTRATO AG 
    # 03298 - PAC CONTRATO AG 
    # 04227 - CORREIOS MINI ENVIOS CTR AG
    # b = correios.delivery_forecast(['03220', '03298', '04227'], '33110580', '33145160','05/04/2024', '05/04/2024')
    print(a)    


    
    

