function Redirect()
    {
        if(window.location.pathname !== "/"){
            window.location="/";
        }
    }
setTimeout('Redirect()', 60000);