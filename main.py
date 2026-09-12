import http.server
import socketserver
import json
import math

PORT = 8000

class CalculatorHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        # Отдаем index.html при заходе на корень http://localhost:8000
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

    def do_POST(self):
        """Обработка API запросов от клиентской части"""
        if self.path == '/api/calculate':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data.decode('utf-8'))
                req_type = data.get('type')

                # Базовые арифметические операции
                if req_type == 'expression':
                    expr = data.get('expression', '')
                    res = self.evaluate_expression(expr)
                    self.send_json_response({'result': res})

                # Тригонометрические функции
                elif req_type == 'trig':
                    func = data.get('func')
                    val = float(data.get('value', 0))
                    rad = math.radians(val)  # перевод градусов в радианы

                    if func == 'sin':
                        res = math.sin(rad)
                    elif func == 'cos':
                        res = math.cos(rad)
                    elif func == 'tan':
                        if abs(val % 180) == 90:
                            raise ValueError("tan(90°) не существует")
                        res = math.tan(rad)
                    else:
                        raise ValueError("Неизвестная функция")

                    self.send_json_response({'result': round(res, 10)})

                else:
                    self.send_json_error("Некорректный тип запроса")

            except ZeroDivisionError:
                self.send_json_error("Нельзя делить на 0")
            except ValueError as e:
                self.send_json_error(str(e) if str(e) else "Ошибка ввода")
            except Exception:
                self.send_json_error("Ошибка вычислений")
        else:
            self.send_error(404, "File Not Found")

    def evaluate_expression(self, expr):
        """Безопасное вычисление выражений на сервере"""
        allowed_chars = set("0123456789.+-*/() ")
        if not all(c in allowed_chars for c in expr):
            raise ValueError("Недопустимые символы")

        code = compile(expr, "<string>", "eval")
        if code.co_names:
            raise ValueError("Использование функций запрещено")

        res = eval(code, {"__builtins__": {}}, {})
        
        if isinstance(res, (int, float)):
            if math.isnan(res) or math.isinf(res):
                raise ZeroDivisionError()
            return round(res, 10) if isinstance(res, float) else res
        raise ValueError("Ошибка операции")

    def send_json_response(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def send_json_error(self, message):
        self.send_json_response({'error': message}, code=400)


if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), CalculatorHandler) as httpd:
        print(f"Сервер запущен: http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nСервер остановлен.")