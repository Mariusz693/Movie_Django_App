from django.shortcuts import render
from django.views.generic import View

from .models import Movie

# Create your views here.


class IndexView(View):
    
    """
    Return Base View
    """
    def get(self, request):

        movies = Movie.objects.all()[:10]
        return render(
            request=request,
            template_name='movie_app/index.html',
            context={
                'movies': movies,
            }
        )
