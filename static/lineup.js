document.addEventListener("DOMContentLoaded", function() {

    function updateAvailablePlayers() {
        var allPlayers = [];
        document.querySelectorAll('#availability-form input[type="checkbox"]').forEach(function(checkbox) {
            if (checkbox.checked) {
                var playerId = checkbox.value;
                var playerName = document.querySelector('label[for="'+ checkbox.id +'"]').textContent;
                allPlayers.push({id: playerId, name: playerName});
            }
        });

        document.querySelectorAll('#lineup-form select').forEach(function(select) {
            // Get currently selected player
            var selectedPlayerId = select.value;

            // Get all players who haven't been selected in other positions
            var availablePlayers = allPlayers.filter(function(player) {
                // A player is available if they're not selected in any other position,
                // or if they're the currently selected player in this position
                return !isPlayerSelected(player.id) || player.id === selectedPlayerId;
            });

            // Clear existing options
            select.innerHTML = '';

            // Add 'Player' as the default unselectable option
            var defaultOption = document.createElement('option');
            defaultOption.value = "";
            defaultOption.text = "Player";
            defaultOption.disabled = true;
            defaultOption.selected = true;
            select.appendChild(defaultOption);

            // Add new options
            availablePlayers.forEach(function(player) {
                var option = document.createElement('option');
                option.value = player.id;
                option.text = player.name;
                if (player.id === selectedPlayerId) {
                    // If this player is currently selected in this position, keep them selected
                    option.selected = true;
                }
                select.appendChild(option);
            });
        });
    }

    // This function checks if a player is selected in any position other than the current one
    function isPlayerSelected(playerId) {
        var selectedPlayerIds = Array.from(document.querySelectorAll('#lineup-form select'))
            .map(function(select) { return select.value; });
        return selectedPlayerIds.includes(playerId);
    }

    // Call updateAvailablePlayers whenever a player is selected
    document.querySelectorAll('#lineup-form select').forEach(function(select) {
        select.addEventListener('change', updateAvailablePlayers);
    });

    // Also call updateAvailablePlayers when the page loads
    updateAvailablePlayers();
    
});