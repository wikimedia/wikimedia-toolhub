// Django's regex validation expects all whitespace to be encoded
const RE_URL_VALID_BASIC = /^https?:\/\/[^\s]+$/;

/**
 * Is the given input a valid HTTP URL?
 *
 * @param {string} input - input to validate
 * @return {boolean} True if URL is valid, false otherwise
 */
export function isValidHttpUrl( input ) {
	if ( !RE_URL_VALID_BASIC.test( input ) ) {
		return false;
	}

	try {
		// eslint-disable-next-line no-unused-vars
		const url = new URL( input );
		return true;
	} catch ( _ ) {
		return false;
	}
}
