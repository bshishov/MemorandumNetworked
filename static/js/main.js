$(document).ready(function(){
    // the "href" attribute of .modal-trigger must specify the modal ID that wants to be triggered
    $('.modal-trigger').leanModal();
  });


var setRelation = function(relation) {
    $( "input[name='relation']" ).val(relation);
    $( "input[name='relation']" ).trigger('autoresize');
};