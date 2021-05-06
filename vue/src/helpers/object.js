/**
 * Remove null and undefined values from an object.
 *
 * @param {Object} obj - object to filter
 * @return {Object} new object
 */
export function filterEmpty( obj ) {
	if ( arguments.length === 0 ) {
		return {};
	}
	if ( obj === undefined || obj === null ) {
		return {};
	}
	return Object.keys( obj )
		.filter( ( key ) => obj[ key ] !== null && obj[ key ] !== undefined )
		.reduce( ( accum, key ) => ( { ...accum, [ key ]: obj[ key ] } ), {} );
}
