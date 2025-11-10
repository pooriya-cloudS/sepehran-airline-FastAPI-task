Feature: Flight Management API
  As a user of the Flights API
  I want to be able to create, view, update, and deactivate flights
  So that I can manage active flight data while preserving historical records.

  Background:
    Given the API is running
    And the database is initialized and empty

  Scenario: Create a new flight record successfully
    Given I have valid flight data:
      | flight_number | origin | destination | departure_time      | arrival_time        |
      | IR123         | Tehran | Istanbul    | 2025-11-12T08:00:00 | 2025-11-12T10:30:00 |
    When I send a POST request to "/flights/"
    Then the response status code should be 201
    And the response JSON should include:
      | status  | message                       |
      | success | Flight created successfully   |

  Scenario: Retrieve a paginated and sorted list of active flights
    Given multiple flights exist in the system
    And all have "is_active" set to true
    When I send a GET request to "/flights/?page=1&limit=5&sort_by=departure_time"
    Then the response status code should be 200
    And the response should include a list of active flights sorted by departure_time

  Scenario: Filter flights by origin using query parameters
    Given there are flights departing from multiple origins
    When I send a GET request to "/flights/?origin=Tehran"
    Then the response should only include flights with origin "Tehran"

  Scenario: Update an existing flight record
    Given a flight with flight_number "IR123" already exists
    When I send a PUT request to "/flights/IR123" with new destination "Ankara"
    Then the response status code should be 200
    And the response message should be "Flight updated successfully"

  Scenario: Deactivate a flight instead of deleting
    Given a flight with flight_number "IR123" exists and is_active is true
    When I send a PATCH request to "/flights/IR123/deactivate"
    Then the response status code should be 200
    And the response JSON should include:
      | status  | message                    |
      | success | Flight deactivated successfully |
    And the "is_active" attribute of that flight should now be false

  Scenario: Handle invalid flight creation request (validation error)
    Given I have incomplete flight data:
      | flight_number | origin |
      | IR999         | Tehran |
    When I send a POST request to "/flights/"
    Then the response status code should be 422
    And the response JSON should include a validation error message
