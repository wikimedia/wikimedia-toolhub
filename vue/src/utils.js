/**
 * Ensure that something is an array.
 *
 * Reduce clutter and repeated code when handling an input that might be
 * either a scalar or an array with this utility function. Implements this
 * algorithm:
 *
 * - If called with no arguments: return []
 * - If called with one argument that is undefined or null: return []
 * - If called with one argument that is an Array: return argument
 * - Otherwise: return an array containing all arguments
 *
 * @param {...*} [value] - Thing to ensure is wrapped in an array
 * @return {Array} Guaranteed to be an Array
 */
export function ensureArray( value ) {
	if ( arguments.length === 0 ) {
		return [];
	}
	if ( arguments.length === 1 ) {
		if ( value === undefined || value === null ) {
			return [];
		}
		if ( Array.isArray( value ) ) {
			return value;
		}
	}
	return Array.prototype.slice.call( arguments );
}
