from django.shortcuts import render,get_object_or_404,redirect
from .models import Item,Category,Comment,Like
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .forms import NewItemForm,EditItemForm,CommentForm

# Create your views here.
def items(request):
    query = request.GET.get('query','')
    items = Item.objects.all()
    categories= Category.objects.all()
    category_id=request.GET.get('category',0)

    if category_id:
        items = items.filter(category_id=category_id)

    if query:
        items = items.filter(Q(name__icontains=query) | Q(description__icontains=query))

    return render(request,'item/items.html',{
        'items':items,
        'query':query,
        'categories':categories,
        'category_id':int(category_id)
    })

@login_required
def detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    related_items = Item.objects.filter(category=item.category).exclude(pk=pk)[0:3]
    
    # 获取所有评论并过滤出父评论
    parent_comments = item.comments.filter(parent__isnull=True)

    # 判断当前用户是否已经点赞
    user_has_liked = Like.objects.filter(user=request.user, item=item).exists()

    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)

        if form.is_valid():
            parent_comment = None
            if form.cleaned_data.get('reply_to'):
                parent_comment = get_object_or_404(Comment, pk=form.cleaned_data['reply_to'])
            comment = form.save(commit=False)
            comment.item = item
            comment.user = request.user
            comment.parent = parent_comment
            comment.save()
            return redirect('item:detail', pk=item.id)
    else:
        form = CommentForm()

    form.fields['text'].widget.attrs.update({'class': 'w-full h-10 p-2 text-sm border border-gray-300 rounded-md'})

    return render(request, 'item/detail.html', {
        'item': item,
        'related_items': related_items,
        'form': form,
        'parent_comments': parent_comments,
        'user_has_liked': user_has_liked,  # 传递用户是否点赞的信息
    })


@login_required
def new(request):
    if request.method=='POST':
        form = NewItemForm(request.POST,request.FILES)

        if form.is_valid():
            item=form.save(commit=False)
            item.created_by = request.user
            item.save()

            return redirect('item:detail',pk=item.id)
    else:
        form=NewItemForm()

    return render(request,'item/form.html',{
        'form':form,
        'title':'New item',
    })

@login_required
def delete(request,pk):
    item = get_object_or_404(Item,pk=pk,created_by=request.user)
    item.delete()

    return redirect('dashboard:index')

@login_required
def edit(request, pk):
    item = get_object_or_404(Item, pk=pk, created_by=request.user)

    if request.method == 'POST':
        form = EditItemForm(request.POST, request.FILES, instance=item)

        if form.is_valid():
            form.save()

            return redirect('item:detail', pk=item.id)
    else:
        form = EditItemForm(instance=item)

    return render(request, 'item/form.html', {
        'form': form,
        'title': 'Edit item',
    })

@login_required
def toggle_like(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    user = request.user

    # 判断用户是否已点赞
    like = Like.objects.filter(user=user, item=item).first()

    if like:
        # 如果已点赞，删除该记录（取消点赞）
        like.delete()
    else:
        # 如果未点赞，创建新的点赞记录
        Like.objects.create(user=user, item=item)

    # 跳转回当前 item 的详情页面
    return redirect('item:detail', pk=item.id)

@login_required
def delete_comment(request, item_id, comment_id):
    item = get_object_or_404(Item, id=item_id)
    comment = get_object_or_404(Comment, id=comment_id)

    # 确保只有评论的作者才能删除评论
    if comment.user == request.user:
        comment.delete()

    return redirect('item:detail', pk=item.id)  # 删除后回到商品详情页面