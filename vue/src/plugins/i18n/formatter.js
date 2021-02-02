import Banana from 'banana-i18n';

export default class BananaFormatter {

	/**
	 * Constructor.
	 *
	 * @param {string} locale - current locale
	 */
	constructor( locale ) {
		this.setLocale( locale );
	}

	setLocale( locale ) {
		this.locale = locale;
		this.parser = new Banana( this.locale ).parser;
	}

	/**
	 * Interpolate a message.
	 *
	 * @param {string} message - message string
	 * @param {Object | Array<any> | undefined} values - values to interpolate
	 * @return {Array<any>} interoplated values
	 */
	interpolate( message, values ) {
		if ( !values ) {
			return [ message ];
		}
		// Vue-i18n allows passing values as either an array or as an object.
		// Banana only supports positional arguments, and js does not
		// guarantee iteration order for objects. If we are passed an object,
		// emit a warning to the console and pretend we did not get any
		// values.
		if ( !Array.isArray( values ) ) {
			if ( process.env.NODE_ENV !== 'production' ) {
				// eslint-disable-next-line no-console
				console.warn(
					'BananaFormatter only allows array arguments. Ignoring %o',
					values
				);
			}
			values = [];
		}
		return [ this.parser.parse( message, values ) ];
	}
}
