// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TournamentManager {
    
    // Structure to store tournament information
    struct Tournament {
        uint256 id;
        uint256[] users_id; // List of user id participating in the tournament
        // Add a minimum length to create a tournament (4)?
        mapping(uint256 => uint256) scores; // Mapping of user id to their score
        bool exists; // Flag to check if tournament exists
    }


    // Mapping to store tournaments by ID
    mapping(uint256 => Tournament) public tournaments;

    // Event to notify when a tournament is created or a score is updated
    event TournamentCreated(uint256 tournamentId, uint256[] users_id);
    event ScoreUpdated(uint256 tournamentId, uint256 user, uint256 newScore);

    // Function to create a tournament
    function createTournament(uint256 _tournamentId, uint256[] memory _users_id) public {
        require(!tournaments[_tournamentId].exists, "Tournament already exists");

        Tournament storage newTournament = tournaments[_tournamentId];
        newTournament.id = _tournamentId;
        newTournament.users_id = _users_id;
        newTournament.exists = true;

        emit TournamentCreated(_tournamentId, _users_id);
    }

    // Function to update the score of a user in a tournament
    function updateScore(uint256 _tournamentId, uint256 _user, uint256 _score) public {
        require(tournaments[_tournamentId].exists, "Tournament does not exist");
        
        Tournament storage tournament = tournaments[_tournamentId];
        require(isUserInTournament(tournament, _user), "User is not in the tournament");

        tournament.scores[_user] = _score;

        emit ScoreUpdated(_tournamentId, _user, _score);
    }

    // Function to get the score of a user in a tournament
    function getScore(uint256 _tournamentId, uint256 _user) public view returns (uint256) {
        require(tournaments[_tournamentId].exists, "Tournament does not exist");

        Tournament storage tournament = tournaments[_tournamentId];
        require(isUserInTournament(tournament, _user), "User is not in the tournament");

        return tournaments[_tournamentId].scores[_user];
    }

    // Internal function to check if a user is in the tournament
    function isUserInTournament(Tournament storage tournament, uint256 _user) internal view returns (bool) {
        for (uint256 i = 0; i < tournament.users_id.length; i++) {
            if (tournament.users_id[i] == _user) {
                return true;
            }
        }
        return false;
    }

    // Get tournament winner
    function getWinner(uint256 _tournamentId) public view returns (uint256) {
        require(tournaments[_tournamentId].exists, "Tournament does not exist");

        Tournament storage tournament = tournaments[_tournamentId];
        require(tournament.users_id.length > 0, "No users in the tournament");

        uint256 winner = tournament.users_id[0];
        uint256 maxScore = tournament.scores[winner];

        for (uint256 i = 1; i < tournament.users_id.length; i++) {
            uint256 score = tournament.scores[tournament.users_id[i]];
            if (score > maxScore) {
                winner = tournament.users_id[i];
                maxScore = score;
            }
        }

        require(maxScore == 2, "No winner in the tournament");

        return winner;
    }
}
