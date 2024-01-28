var viewBtns = document.getElementsByClassName('view-product');

for (var i = 0; i < viewBtns.length; i++) {
    viewBtns[i].addEventListener('click', function(){
        var productId = this.dataset.product;
        console.log('View Product ID:', productId);

        // Redirecting to the product page
        window.location.href = '/product/' + productId;
    });
}
