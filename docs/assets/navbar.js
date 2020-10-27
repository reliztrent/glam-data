$('.sidebar .nav-link').click(function(){
    $('.glow').removeClass('glow');
    var anchor_href = $(this).attr('href');
    var anchor = anchor_href.split('#')[anchor_href.split('#').length-1];
    var anchor_id = $('#' + anchor);
    anchor_id.addClass('glow');
    setTimeout(function () {
        anchor_id.removeClass('glow');
    }, 3000); /This should match the number of seconds on the glow css class/
})

/* zoom modals
*/
var emptyModal = $('<div id="zoomModal" class="modal fade" role="dialog" tabindex="-1"></div>');
$('main').append(emptyModal);

$('.zoom').hover(function(){
	$(this).attr('data-target','zoomModal');
	var modalCard = document.getElementById('zoomModal');
	var card = $(this).closest(".card");
	card.clone().appendTo( '#zoomModal');
});