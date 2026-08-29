    st.toast('¡Transferencias completadas, gran trabajo esta semana! 🎉', icon='✨')
    
    # Inyección de HTML puro con iFrame (Para forzar autoplay en algunos navegadores)
    st.components.v1.html(
        '''
        <iframe src="https://actions.google.com/sounds/v1/foley/cash_register_kaching.ogg" allow="autoplay" style="display:none" id="iframeAudio">
        </iframe>
        <audio autoplay="true" src="https://actions.google.com/sounds/v1/foley/cash_register_kaching.ogg"></audio>
        <script>
            // Intento con JS puro
            var audio = new Audio('https://actions.google.com/sounds/v1/foley/cash_register_kaching.ogg');
            audio.play().catch(function(error) {
                console.log("Autoplay bloqueado por el navegador: ", error);
            });
        </script>
        ''', 
        width=0, height=0
    )
    
    st.session_state.exito_trigger = False
