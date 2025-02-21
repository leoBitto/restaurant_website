# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from .forms import DishForm
from .models import Dish, DishType

class MenuView(View):
    template_name = 'menu_management/menu.html'


    def get(self, request, *args, **kwargs):
        # Singola query per tutti i piatti
        all_dishes = Dish.get_current_version()
        
        # Organizziamo i piatti per tipo
        context = {
            'entrees': all_dishes.filter(dish_type=DishType.ENTREE),
            'first_dishes': all_dishes.filter(dish_type=DishType.FIRST_DISH),
            'second_dishes': all_dishes.filter(dish_type=DishType.SECOND_DISH),
            'side_dishes': all_dishes.filter(dish_type=DishType.SIDE_DISH),
            'desserts': all_dishes.filter(dish_type=DishType.DESSERT),
            'others': all_dishes.filter(dish_type=DishType.OTHER),
        }
        
        return render(request, self.template_name, context)

class WineView(View):
    template_name = 'menu_management/wine.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            'title': 'Il nostro Vino',
        })

class DishView(LoginRequiredMixin, View):
    template_name = 'menu_management/backoffice/menu_backoffice.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            'dish_data': self._get_dish_data(),
            'dish_form': DishForm(),
        })

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        dish_id = kwargs.get('pk')
        
        if action == 'create':
            return self._handle_create(request)
        
        if dish_id:
            dish = get_object_or_404(Dish, id=dish_id, is_deleted=False)
            if action == 'update':
                return self._handle_update(request, dish)
            elif action == 'delete':
                return self._handle_delete(request, dish)
        
        messages.error(request, 'Azione non valida.')
        return redirect('menu_management:menu_backoffice')

    def _get_dish_data(self):
        return {
            dish_type: [
                {
                    'dish': dish,
                    'form': DishForm(instance=dish),
                }
                for dish in Dish.get_current_version(dish_type=dish_type[0])
            ]
            for dish_type in DishType.choices
        }

    def _handle_create(self, request):
        form = DishForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Piatto aggiunto con successo.')
            except Exception as e:
                messages.error(request, f'Errore durante il salvataggio: {str(e)}')
        else:
            self._add_form_errors(request, form)
        return redirect('menu_management:menu_backoffice')

    def _handle_update(self, request, dish):
        form = DishForm(request.POST, instance=dish)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Piatto aggiornato con successo.')
            except ValueError as e:
                messages.error(request, f'Errore durante l\'aggiornamento: {str(e)}')
        else:
            self._add_form_errors(request, form)
        return redirect('menu_management:menu_backoffice')

    def _handle_delete(self, request, dish):
        try:
            dish.delete()
            messages.success(request, 'Piatto eliminato con successo.')
        except Exception as e:
            messages.error(request, f'Errore durante l\'eliminazione: {str(e)}')
        return redirect('menu_management:menu_backoffice')

    def _add_form_errors(self, request, form):
        error_message = ', '.join(
            f'{field}: {error}' 
            for field, errors in form.errors.items() 
            for error in errors
        )
        messages.error(request, f'Si è verificato un errore: {error_message}')
