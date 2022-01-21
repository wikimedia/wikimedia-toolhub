import SwaggerClient from 'swagger-client';

export const OPENAPI_SCHEMA_URL = '/api/schema/';

/**
 * @type {Promise<SwaggerClient>}
 */
export const client = new SwaggerClient( {
	url: OPENAPI_SCHEMA_URL
} );

/**
 * Add common default values to a Request.
 *
 * @param {Object} request - API request details
 * @param {Object} context - Vuex context
 * @param {Object} context.rootState - Cross module state data
 * @return {Object}
 */
export function addRequestDefaults( request, context ) {
	request.method = request.method || 'GET';
	request.headers = request.headers || {};
	if ( !( 'Accept' in request.headers ) ) {
		// eslint-disable-next-line dot-notation
		request.headers[ 'Accept' ] = 'application/json';
	}
	if ( !( 'Accept-Language' in request.headers ) ) {
		const ctx = context.rootState.locale;
		request.headers[ 'Accept-Language' ] = ctx.locale;
	}
	if ( !( 'Content-Type' in request.headers ) ) {
		request.headers[ 'Content-Type' ] = 'application/json';
	}
	if ( request.method.toUpperCase() !== 'GET' ) {
		const ctx = context.rootState.user;
		request.headers[ 'X-CSRFToken' ] = ctx.user.csrf_token;
	}
	return request;
}

/**
 * Extract a failure payload from a rejected API call Promise.
 *
 * If the provided error contains a 'response' member, attempt to parse and
 * return it's body. On failure or any other input, return the provided input
 * error.
 *
 * @param {*} err - rejected Promise return value
 * @return {Object} Parsed JSON error body or raw Error data
 */
export function getFailurePayload( err ) {
	if ( 'response' in err ) {
		try {
			return JSON.parse( err.response.data );
		} catch ( ex ) {}
	}
	return err;
}

/**
 * Construct a URLSearchParams object from a sequence of [key, value] parameters.
 *
 * Items where the value is null or undefined are filtered out of the input.
 *
 * @param {string[][]} params - Sequence of [key, value] parameters
 * @return {URLSearchParams}
 */
export function makeURLQueryParams( params ) {
	return new URLSearchParams(
		params.filter( ( value ) => {
			const val = value[ 1 ];
			return val !== null && val !== undefined;
		} )
	);
}

/**
 * @typedef SwaggerResponse
 * @property {boolean} ok - was response successful (200-299) or not
 * @property {number} status - status code
 * @property {string} statusText - status message
 * @property {string} url - request url
 * @property {Object} headers - response headers
 * @property {string} text - unparsed response body
 * @property {Object|undefined} body - JSON object or undefined
 * @property {Error|undefined} parseError - Serialization error
 */

/**
 * @typedef StatusError
 * @property {string} message - status message
 * @property {number} statusCode - status code
 * @property {SwaggerResponse} response - original response object
 */

/**
 * @typedef InterceptorError
 * @property {string} message - status message
 * @property {number} statusCode - status code
 * @property {Error} responseError - Error thrown in responseInterceptor
 */

/**
 * Make an API call.
 *
 * @async
 * @param {Object} context - Vuex context
 * @param {Object} request - API request details
 * @return {Promise<SwaggerResponse>} A promise for the API call
 * @throws {Error} Network problem or CORS misconfiguration
 * @throws {Error<StatusError>} Status or serialization failure
 * @throws {Error<InterceptorError>} ResponseInterceptor error
 */
export function makeApiCall( context, request ) {
	return SwaggerClient.http( addRequestDefaults( request, context ) );
}

export default makeApiCall;
