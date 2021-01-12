import SwaggerClient from 'swagger-client';

/**
 * Makes an API call.
 *
 * @param {Object} context - Provides access to state
 * @param {Object} request - API request details
 * @return {Object} API response
 */

function makeApiCall( context, request ) {
	request.headers = request.headers || {};
	request.headers[ 'Content-Type' ] = 'application/json';
	if ( request.method !== 'GET' ) {
		request.headers[ 'X-CSRFToken' ] = context.state.user.csrf_token;
	}

	return SwaggerClient.http( request );
}

export default makeApiCall;
