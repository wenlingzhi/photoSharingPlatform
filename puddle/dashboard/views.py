from django.shortcuts import render,get_object_or_404

from item.models import Item,Like

from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    items = Item.objects.filter(created_by=request.user)
    return render(request,'dashboard/index.html',{
        'items':items,
    })


@login_required
def favorite_items(request):
    # 获取当前用户喜欢的所有物品
    liked_items = Like.objects.filter(user=request.user).values_list('item', flat=True)
    items = Item.objects.filter(id__in=liked_items)

    return render(request, 'dashboard/favorate.html', {
        'items': items
    })


