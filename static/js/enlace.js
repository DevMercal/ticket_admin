
    const activeLink = document.querySelector('a.active');

 
    if (activeLink) {
        
        activeLink.addEventListener('click', function(event) {
            
           
            event.preventDefault();

           
            console.log("Already on the Dashboard. Preventing full reload.");
        });
    }


     function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('-translate-x-full');
        }