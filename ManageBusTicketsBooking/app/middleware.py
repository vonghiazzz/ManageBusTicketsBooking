from django.shortcuts import render
class CustomErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 404:
            return render(request, 'app/errors.html', {
                'error_code': 404,
                'error_message': 'Page not found'
            })
        elif response.status_code == 403:
            return render(request, 'app/errors.html', {
                'error_code': 403,
                'error_message': 'Forbidden'
            })
        elif response.status_code == 500:
            return render(request, 'app/errors.html', {
                'error_code': 500,
                'error_message': 'Internal Server Error'
            })
        elif response.status_code == 400:
            return render(request, 'app/errors.html', {
                'error_code': 400,
                'error_message': 'Bad Request'
            })
        return response
