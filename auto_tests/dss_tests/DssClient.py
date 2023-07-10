import requests
import base64
import os

class DssClient:
    def __init__(self, login: str, password: str, dssAddress: str, tspAddress: str) -> None:
        self.__token = self.auth(login, password, dssAddress)
        self.__cert_id = self.get_cert_id(self.__token, dssAddress)
        self.__dssAddress = dssAddress
        self.__tspAddress = tspAddress
        self.__path = "auto_tests/dss_tests/"
    
    @staticmethod
    def auth(login: str, password: str, dssAddress: str) -> str:
        url = dssAddress + "/usersidp/oauth/token"
        
        content = {
            "client_id": "linus.csp",
            "grant_type": "password",
            "username": login,
            "password": password
        }
        
        response: dict = requests.post(url, data=content).json()
        
        token = response.get("access_token", None)
        
        if token is None:
            print(response["error_description"])
        
        return token
    
    @staticmethod
    def get_cert_id(token: str, dssAddress: str) -> str:
        url = dssAddress + "/servss/rest/api/certificates"
        
        headers = {
            'Authorization': f'Bearer {token}'
        }
        
        response: list[dict] | dict = requests.get(url, headers=headers).json()
        
        if isinstance(response, dict) and response.get("Message", None) is not None:
            print(response["Message"])
            return None
        elif isinstance(response, list) and len(response) == 0:
            print("User don't have any certificates")
            return None
        
        cert_id = response[0]["ID"]
        return cert_id
    
    @staticmethod
    def file_to_bytes(file_path: str) -> bytes:
        with open(file_path, 'rb') as file:
            pdf_bytes = file.read()
        return pdf_bytes
    
    def __sign_documents(self, files: list[str], dir: str, file_type: str, **kwargs) -> list:
        files = map(lambda x: os.path.join(self.__path, dir, x), files)
        original_content = list(map(self.file_to_bytes, files))
        
        result = []

        headers = {
            'Authorization': f'Bearer {self.__token}'
        }
        
        for data in original_content:
            url = self.__dssAddress + "/servss/rest/api/documents"
            hash_base64 = base64.b64encode(data).decode("utf-8")

            payload = {
                "Content": hash_base64,
                "Signature": {
                    "Type": file_type,
                    "Parameters": {
                        "TSPAddress": self.__tspAddress,
                        **kwargs
                    },
                    "CertificateId": self.__cert_id,
                    "PinCode": ""
                }
            }

            response = requests.post(url, json=payload, headers=headers)
            response_content = response.json()

            result.append(response_content)

        return result
    
    def sign_documents_pdf(self, files: list[str]) -> list:
        return self.__sign_documents(files, "pdf", "PDF", PDFFormat="CAdES")
    
    def sign_documents_office(self, files: list[str]) -> list:
        return self.__sign_documents(files, "office", "MSOffice")
    
    def sign_documents_cades_xlt1(self, files: list[str]) -> list:
        return self.__sign_documents(files, "cades", "CAdES", CADESType="XLT1", IsDetached=True)
    
    def sign_documents_cades_xlt1_cosign(self, files: list[str], original_document: list[str]) -> list:
        original_document = os.path.join("auto_tests/dss_tests/", "cades", original_document[0])
        with open(original_document, 'rb') as file:
            original_document_bytes = file.read()
        original_document_bytes = base64.b64encode(original_document_bytes).decode("utf-8")
        return self.__sign_documents(files, "cades", "CAdES", CADESType="XLT1", IsDetached=True,
                                     CmsSignatureType="Cosign", OriginalDocument=original_document_bytes)
    
    
    def __verify_signature(self, signature_type: str, document, signature, dir, isHash=False, hashAlgorithm="GR 34.11-2012 256") -> dict:
        url = self.__dssAddress + "/verify/rest/api/signatures"
        
        if document:
            document = os.path.join(self.__path, dir, document)
            document = self.file_to_bytes(document)
            print(document)
        signature = os.path.join(self.__path, dir, signature)
        signature = self.file_to_bytes(signature)
        
        documentBase64 = base64.b64encode(document).decode("utf-8") if document else ""
        signatureBase64 = base64.b64encode(signature).decode("utf-8") if signature else ""
        
        payload = {
            'Content': signatureBase64,
            'SignatureType': signature_type,
            'VerifyParams': {
                'ExtractContent': True,
                'VerifyAll': True
            }
        }

        if signature_type not in ["MSOffice", "PDF"]:
            payload['Source'] = documentBase64

        if isHash:
            payload['VerifyParams']['Hash'] = isHash

        if signature_type in ["CAdES", "CMS"]:
            payload['VerifyParams']['IsDetached'] = True
            if isHash:
                payload['VerifyParams']['HashAlgorithm'] = hashAlgorithm
        
        response = requests.post(url, json=payload)

        result = response.json()
        
        return result
    
    def verify_signature_pdf(self, signature) -> dict:
        return self.__verify_signature("PDF", None, signature, "pdf")
    
    def verify_signature_office(self, signature) -> dict:
        return self.__verify_signature("MSOffice", None, signature, "office")
    
    def verify_detached_signature(self, document, signature) -> dict:
        return self.__verify_signature("CAdES", document, signature, "cades")
        