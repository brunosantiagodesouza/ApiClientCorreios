
import base64
import requests


class pyCorreios:
    default_url = 'https://api.correios.com.br/'
    def __init__(self, user, acess_code, post_card, contract):
        self.url = ''
        self.user =user
        self.acess_code = acess_code
        self.post_card = post_card
        self.contract = contract
        

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
                return {
                'token_refresh_date' :respose_json['emissao'],
                'token_expire_date' :respose_json['expiraEm'],
                'token': respose_json['token']
                }
            
            elif(respose.status_code == 400):
                print('Erro de validação verifique se todas informações foram passadas corretamente')

            elif(respose.status_code == 500):
                print('Erro no servidor , tente novamente mais tarde')
            return None
        
        elif(mode == 'contrato'):

            self.url = f'{self.default_url}token/v1/autentica/contrato'
            data = {'numero':self.contract}
            
            respose = requests.post(url = self.url, json= data, headers= header)
            
            if respose.status_code == 201:
                respose_json = respose.json()
                return {
                'token_refresh_date' :respose_json['emissao'],
                'token_expire_date' :respose_json['expiraEm'],
                'token': respose_json['token']
                }
            
            elif(respose.status_code == 400):
                print('Erro de validação verifique se todas informações foram passadas corretamente')

            elif(respose.status_code == 500):
                print('Erro no servidor , tente novamente mais tarde')

        elif(mode == ''):
            
            self.url = f'{self.default_url}token/v1/autentica'
            
            respose = requests.post(url = self.url, json= '', headers= header)
            
            if respose.status_code == 201:
                respose_json = respose.json()
                return {
                'token_refresh_date' :respose_json['emissao'],
                'token_expire_date' :respose_json['expiraEm'],
                'token': respose_json['token']
                }
            
            elif(respose.status_code == 400):
                print('Erro de validação verifique se todas informações foram passadas corretamente')

            elif(respose.status_code == 500):
                print('Erro no servidor , tente novamente mais tarde')
        
        else:
            raise ValueError("Modo de autenticação não reconhecido.")



        



if __name__ == '__main__':
    from dotenv import dotenv_values

    config = dotenv_values(".venv\.env")
    
    user =config.get('USER')
    acess_token = config.get('ACESS_TOKEN')
    post_card = config.get('POST_CARD')
    contract = config.get('N_CONTRACT')
    correios =pyCorreios(user, acess_token, post_card, contract)
    fresh_token1= correios.refresh_token()
    print(fresh_token1)
    fresh_token1= correios.refresh_token('contrato')
    print(fresh_token1)
    fresh_token1= correios.refresh_token('')
    print(fresh_token1)


    
    

