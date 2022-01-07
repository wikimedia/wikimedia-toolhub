/**
 * Is the given input a valid HTTP URL?
 *
 * @param {string} input - input to validate
 * @return {boolean} True if URL is valid, false otherwise
 */
export function isValidHttpUrl( input ) {
	// Django's regex validation expects all whitespace to be encoded
	if ( /\s/.test( input ) ) {
		return false;
	}

	let url;
	try {
		url = new URL( input );
	} catch ( _ ) {
		return false;
	}

	return url.protocol === 'https:' || url.protocol === 'http:';
}
