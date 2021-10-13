import { subject as addSubject } from '@casl/ability';

export const TOOL_SUBJECT = 'toolinfo/tool';
export const URL_SUBJECT = 'crawler/url';
export const APP_SUBJECT = 'oauth2_provider/application';
export const TOKEN_SUBJECT = 'oauth2_provider/accesstoken';
export const VERSION_SUBJECT = 'reversion/version';
export const LIST_SUBJECT = 'lists/toollist';

/**
 * Set a CASL subject type on a POJO object or object array.
 *
 * @param {string} subject - subject type (e.g. 'toolinfo/tool')
 * @param {Object|Object[]} pojo - plain old js object to decorate
 * @return {Object|Object[]}
 */
export function setPOJOSubjectType( subject, pojo ) {
	if ( Array.isArray( pojo ) ) {
		return pojo.map( ( item ) => addSubject( subject, item ) );
	}
	return addSubject( subject, pojo );
}

/**
 * Mark a POJO or array of POJOs as a tool model.
 *
 * @param {Object|Object[]} pojo
 * @return {Object|Object[]}
 */
export function asTool( pojo ) {
	return setPOJOSubjectType( TOOL_SUBJECT, pojo );
}

/**
 * Mark a POJO or array of POJOs as a URL model.
 *
 * @param {Object|Object[]} pojo
 * @return {Object|Object[]}
 */
export function asUrl( pojo ) {
	return setPOJOSubjectType( URL_SUBJECT, pojo );
}

/**
 * Mark a POJO or array of POJOs as an application model.
 *
 * @param {Object|Object[]} pojo
 * @return {Object|Object[]}
 */
export function asApp( pojo ) {
	return setPOJOSubjectType( APP_SUBJECT, pojo );
}

/**
 * Mark a POJO or array of POJOs as a token model.
 *
 * @param {Object|Object[]} pojo
 * @return {Object|Object[]}
 */
export function asToken( pojo ) {
	return setPOJOSubjectType( TOKEN_SUBJECT, pojo );
}

/**
 * Mark a POJO or array of POJOs as a version model.
 *
 * @param {Object|Object[]} pojo
 * @return {Object|Object[]}
 */
export function asVersion( pojo ) {
	return setPOJOSubjectType( VERSION_SUBJECT, pojo );
}

/**
 * Mark a POJO or array of POJOs as a list model.
 *
 * @param {Object|Object[]} pojo
 * @return {Object|Object[]}
 */
export function asList( pojo ) {
	return setPOJOSubjectType( LIST_SUBJECT, pojo );
}
