from auto_tests.dss_tests.DssClient import DssClient
from analysis.models import Result
from auto_tests.models import Test
import time
import datetime
import json
import pytz


class CheckSignDocuments: 
    client = DssClient("6720ryzhikov", "r6SZv2p4", "https://dss.linus.su", "http://qs.cryptopro.ru/tsp/tsp.srf")
    
    __methods = {
        "pdf": client.sign_documents_pdf,
        "office": client.sign_documents_office,
        "cades": client.sign_documents_cades_xlt1,
        "cades_cosign": client.sign_documents_cades_xlt1_cosign
    }
    
    def __init__(self, type_sign: str, files_path: list[str], expected_result: list[bool], test: Test, original_document = None, *args, **kwargs) -> None:
        assert len(files_path) == len(expected_result), "The lengths of the list of files and the expected results should be equal"
        assert type_sign in self.__methods, f"Sign type must be in {list(self.__methods)}"
        self.type_sign = type_sign
        self.files_path = files_path
        self.expected_result = expected_result
        self.method = self.__methods[type_sign]
        self.test = test
        self.original_document = original_document
    
    def run(self) -> Result:
        date = datetime.datetime.now()
        date = date.astimezone(pytz.timezone('Europe/Moscow'))
        test_result = True
        errors = [''] * len(self.expected_result)
        start = time.time()
        if self.type_sign == "cades_cosign":
            response = self.method(self.files_path, self.original_document)
        else:
            response = self.method(self.files_path)
        end = time.time()
        for i, (res, exp) in enumerate(zip(response, self.expected_result)):
            is_sign = isinstance(res, str)
            if is_sign != exp:
                test_result = False
                if exp:
                    errors[i] = json.dumps(res)
                else:
                    errors[i] = "The document does not have to be signed"
        work_time = end - start
        test_error = '\n'.join(errors)
        result = Result(test=self.test, passed=test_result, test_error=test_error,
                        server_timeout=datetime.timedelta(seconds=work_time), date=date)
        result.save()
        return result
        
        
class CheckVerifySignature:
    client = DssClient("6720ryzhikov", "r6SZv2p4", "https://dss.linus.su", "http://qs.cryptopro.ru/tsp/tsp.srf")

    __methods = {
        "pdf": client.verify_signature_pdf,
        "office": client.verify_signature_office,
        "cades": client.verify_detached_signature
    }
    
    def __init__(self, type_sign: str, files_path: str, signature_path: str | None, expected_result: bool, test: Test, *args, **kwargs) -> None:
        assert type_sign in self.__methods, f"Sign type must be in {list(self.__methods)}"
        if type_sign == "cades":
            assert files_path is not None
        self.type_sign = type_sign
        self.files_path = files_path
        self.signature_path = signature_path
        self.expected_result = expected_result
        self.method = self.__methods[type_sign]
        self.test = test
    
    def run(self) -> Result:
        date = datetime.datetime.now()
        test_result = True
        error = ''
        start = time.time()
        if self.type_sign != "cades":
            response = self.method(self.files_path)
        else:
            response = self.method(self.files_path, self.signature_path)
        end = time.time()
        work_time = end - start
        if isinstance(response, dict):
            res = response.get("Result", None)
        elif isinstance(response, list) and isinstance(response[0], dict):
            res = response[0].get("Result", None)
        else:
            res = None
        if res is None or res != self.expected_result:
            test_result = False
            error = json.dumps(response)
        result = Result(test=self.test, passed=test_result, test_error=error,
                        server_timeout=datetime.timedelta(seconds=work_time), date=date)
        result.save()
        return result