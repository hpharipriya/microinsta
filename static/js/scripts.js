    function showAddForm(){
        //$("a").toggleClass("add_form");
        $('.add_form').show();
    }
    function closeAddForm(){
        $('.add_form').hide();
    }
    function openCBox(id){
        $('.cbox'+id).show();
    }
    function showNotif(){
        $('.notif').show();
        $('.notif').css("display","block")
    }
    function closeNotif(){
        $('.notif').hide();
        $('.notif').css("display","none")
    }