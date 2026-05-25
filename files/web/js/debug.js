function poll_success(singleShot, data){
  // Hide the offline modal
  hideOfflineModal()

  poll_delay = poll_delay_default

  // Schedule the next polling
  if ( !singleShot ){
    setTimeout(function(){doPoll( false ); }, poll_delay);
  }
}

function initialize_button_handlers(){
  $('.debug_button_container .cycleChevronButton').click(function() {
      const chevron_number = $(this).attr('chevron_number');

      $.post({
          url: 'stargate/do/chevron_cycle',
          data: JSON.stringify({
              chevron_number: chevron_number
          }),
          contentType: 'application/json'
      })
      .fail(function() {
          console.log("Failed to communicate with Stargate")
          $("<div>Failed to communicate with Stargate</div>").dialog();
      });
  });

  $('.debug_button_container .controlButton').click(function() {
      const action = $(this).attr('action');

      // Default: no body
      let payload = null;

      // If this is Incoming simulation, read checkbox and send JSON
      if (action === "simulate_incoming") {
        const cb = document.getElementById("incomingExtended");
        const extended = cb ? cb.checked : false;
        payload = JSON.stringify({ extended: extended });
      }

      $.ajax({
          url: 'stargate/do/' + action,
          type: 'POST',
          data: payload,
          contentType: payload ? 'application/json' : undefined
      })
      .fail(function() {
          console.log("Failed to communicate with Stargate")
          $("<div>Failed to communicate with Stargate</div>").dialog();
      });
  });
}