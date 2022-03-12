'use strict';
import pointer from 'json-pointer';

export const RE_NUMERIC = /^\d+$/;

/**
 * Normalize "empty" values to null.
 *
 * Values considered empty:
 * - undefined
 * - null
 * - '' (empty string)
 * - {} (empty object)
 * - [] (empty array)
 *
 * @param {*} value
 * @return {*|null} Normalized value
 */
export function normalizeEmpty( value ) {
	if ( value === '' || value === null || value === undefined ) {
		return null;
	}
	if (
		( value instanceof Array && value.length === 0 ) ||
		( value instanceof Object && Object.keys( value ).length === 0 )
	) {
		return null;
	}
	return value;
}

/**
 * Is the given value an array, null, or undefined?
 *
 * @param {*} value
 * @return {boolean}
 */
export function isArrayOrNull( value ) {
	return value instanceof Array || value === null || value === undefined;
}

/**
 * Get the length of an array or 0 if not an array.
 *
 * @param {*} arr
 * @return {number}
 */
export function safeArrayLength( arr ) {
	return arr instanceof Array ? arr.length : 0;
}

/**
 * Get the value of a given array index, or undefined.
 *
 * @param {*} arr
 * @param {number} idx
 * @return {*}
 */
export function safeArrayGet( arr, idx ) {
	if ( !( arr instanceof Array ) ) {
		return undefined;
	}
	return idx < arr.length ? arr[ idx ] : undefined;
}

/**
 * Is the given value an object, null, or undefined?
 *
 * @param {*} value
 * @return {boolean}
 */
export function isObjectOrNull( value ) {
	return ( value instanceof Object && !( value instanceof Array ) ) ||
		value === null || value === undefined;
}

/**
 * Get the keys of an object.
 *
 * @param {*} obj
 * @return {string[]}
 */
export function safeObjectKeys( obj ) {
	if ( !( obj instanceof Object ) ) {
		return [];
	}
	return Object.keys( obj );
}

/**
 * Get the value of a property or undefined.
 *
 * @param {*} obj
 * @param {string} key
 * @return {*}
 */
export function safeObjectGet( obj, key ) {
	if ( !( obj instanceof Object ) ) {
		return undefined;
	}
	return obj[ key ];
}

/**
 * Parse a JSON-Pointer into an array of reference tokens.
 *
 * @param {string} path - JSON-Pointer
 * @return {(string|number)[]}
 */
export function parsePath( path ) {
	return pointer.parse( path ).map( ( elm ) => {
		return RE_NUMERIC.test( elm ) ? Number( elm ) : elm;
	} );
}

/**
 * Get a value from a JSON-Pointer or null if not found.
 *
 * @param {Object} ptr - JSON-Pointer object
 * @param {string} path - Path to get
 * @return {*}
 */
export function safePointerGet( ptr, path ) {
	if ( ptr.has( path ) ) {
		return ptr.get( path );
	}
	return null;
}

/**
 * Expand ChangeInfo with complex changed data.
 *
 * Check for an array or object (or array of objects) and convert to a list of
 * ChangeInfo with scalar values. Repeat recursively until both old and new
 * values in all changes are scalar values.
 *
 * @param {ChangeInfo} change - Diff change to examine
 * @return {ChangeInfo[]}
 */
export function expandObjects( change ) {
	const { oldValue, newValue } = change;
	const collector = [];

	if ( isArrayOrNull( oldValue ) && isArrayOrNull( newValue ) ) {
		// Expand to one ChangeInfo per index in longest array
		const maxLength = Math.max(
			safeArrayLength( oldValue ),
			safeArrayLength( newValue )
		);
		for ( let idx = 0; idx < maxLength; idx++ ) {
			collector.push( ...expandObjects(
				{
					path: [ ...change.path, idx ],
					oldValue: safeArrayGet( oldValue, idx ),
					newValue: safeArrayGet( newValue, idx )
				}
			) );
		}

	} else if ( isObjectOrNull( oldValue ) && isObjectOrNull( newValue ) ) {
		// Expand to one ChangeInfo per property in union of properties
		const allKeys = [ ...new Set( [
			...safeObjectKeys( oldValue ),
			...safeObjectKeys( newValue )
		] ) ];
		for ( let idx = 0; idx < allKeys.length; idx++ ) {
			const key = allKeys[ idx ];
			collector.push( ...expandObjects(
				{
					path: [ ...change.path, key ],
					oldValue: safeObjectGet( oldValue, key ),
					newValue: safeObjectGet( newValue, key )
				}
			) );
		}

	} else {
		collector.push( change );
	}
	return collector;
}

/**
 * Compute a changes to render as diff based on a JSON Patch operation.
 *
 * @param {JSONPatchOp} op - JSON Patch operation
 * @param {Object} basisPtr - Source object patch was derived from
 * @param {propertyCallback} formatProp - Callback to format a property value
 * @return {ChangeInfo[]}
 */
export function computeChange( op, basisPtr, formatProp ) {
	const path = parsePath( op.path );
	const ret = [];
	if ( op.op === 'add' ) {
		ret.push( ...expandObjects(
			{
				path: path,
				oldValue: null,
				newValue: formatProp( op.path, op.value )
			}
		) );
		basisPtr.set( op.path, op.value );

	} else if ( op.op === 'remove' ) {
		let newValue = null;
		// Check for array element removal and show new value if removed
		// element was not array tail.
		const parentPath = path.slice( 0, -1 );
		const parent = safePointerGet( basisPtr, parentPath );
		const curIdx = path[ path.length - 1 ];
		if (
			Array.isArray( parent ) &&
			typeof curIdx === 'number' &&
			( curIdx + 1 ) < parent.length
		) {
			const nextPath = [ ...parentPath, curIdx + 1 ];
			newValue = formatProp(
				pointer.compile( nextPath ),
				safePointerGet( basisPtr, nextPath )
			);
		}

		ret.push( ...expandObjects(
			{
				path: path,
				oldValue: formatProp(
					op.path, safePointerGet( basisPtr, op.path )
				),
				newValue: newValue
			}
		) );
		basisPtr.remove( op.path );

	} else if ( op.op === 'replace' ) {
		ret.push( ...expandObjects(
			{
				path: path,
				oldValue: formatProp(
					op.path, safePointerGet( basisPtr, op.path )
				),
				newValue: formatProp( op.path, op.value )
			}
		) );
		basisPtr.set( op.path, op.value );

	} else if ( op.op === 'move' ) {
		const fromProp = formatProp(
			op.from, safePointerGet( basisPtr, op.from )
		);
		ret.push( ...expandObjects(
			{
				path: path,
				oldValue: formatProp(
					op.path, safePointerGet( basisPtr, op.path )
				),
				newValue: fromProp
			}
		) );
		ret.push( ...expandObjects(
			{
				path: parsePath( op.from ),
				oldValue: fromProp,
				newValue: null
			}
		) );
		basisPtr.set( op.path, safePointerGet( basisPtr, op.from ) );
		basisPtr.remove( op.from );

	} else if ( op.op === 'copy' ) {
		const fromVal = safePointerGet( basisPtr, op.from );
		const oldValue = formatProp(
			op.path, safePointerGet( basisPtr, op.path )
		);
		ret.push( ...expandObjects(
			{
				path: path,
				oldValue: oldValue,
				newValue: formatProp( op.path, fromVal )
			}
		) );
		basisPtr.set( op.path, fromVal );

	}
	return ret;
}

/**
 * Compare two change records for sort order.
 *
 * @param {Object} a - First element
 * @param {Object} b - Second element
 * @return {number}
 */
export function compareChanges( a, b ) {
	// Sort by .path component-wise
	const limit = Math.min( a.path.length, b.path.length );
	for ( let i = 0; i < limit; i++ ) {
		if ( a.path[ i ] < b.path[ i ] ) {
			return -1;
		}
		if ( a.path[ i ] > b.path[ i ] ) {
			return 1;
		}
	}
	// Shortest path first
	return a.path.length - b.path.length;
}

/**
 * Compute changes to render as diff based on JSON Patch from API.
 *
 * @param {JSONPatchOp[]} operations - JSON patch operations
 * @param {Object} basis - Source object patch was derived from
 * @param {propertyCallback} formatProp - Callback to format a property value
 * @return {ChangeInfo[]}
 */
export function computeChangeInfo( operations, basis, formatProp ) {
	// Clone basis and wrap for easy pointer operations
	const basisPtr = pointer( JSON.parse( JSON.stringify( basis ) ) );
	const changes = [];

	for ( let i = 0; i < operations.length; i++ ) {
		const op = operations[ i ];
		changes.push( ...computeChange( op, basisPtr, formatProp ) );
	}

	return changes.sort( compareChanges );
}

/**
 * @typedef {Object} JSONPatchOp
 * @property {string} op - Operation to perform
 * @property {string} path - JSON-Pointer to location within document
 * @property {?*} value - Value to add, replace, or test
 * @property {?string} from - JSON-Pointer to location within document
 */
/**
 * @typedef {Object} ChangeInfo
 * @property {(number|string)[]} path - Change path
 * @property {(number|string|boolean|null)} oldValue - Old field value
 * @property {(number|string|boolean|null)} newValue - New field value
 */
/**
 * Callback used to format a property value for display.
 *
 * @callback propertyCallback
 * @param {string} pointer - JSON-Pointer to property
 * @param {*} value - property value
 * @return {*}
 */
