import i18n from '@/plugins/i18n';

/**
 * Generate a list of nodes to output based on message interpolation.
 *
 * This builder takes inspiration from <i18n> and emits an array of values to
 * be added to the DOM. These values can be plain strings or VNode objects
 * that Vue knows how to render as HTML. The list is computed by first getting
 * the localized message _without_ expanding its parameter placeholders. That
 * localized string is then split on the placeholders to produce something
 * like `['string', 'placeholder', 'string', 'placeholder', 'string']`. The
 * code then walks this array and for each element emits either the raw string
 * or the provided argument matching the placeholder position. This output is
 * suitable for use as the children array for a VNode.
 *
 * @param {string} msgKey - Key of message to render
 * @param {Object[]} msgArgs - Arguments to interpolate into message
 * @return {Object[]} List of nodes to emit for rendering
 */
export function buildNodes( msgKey, msgArgs ) {
	// eslint-disable-next-line @intlify/vue-i18n/no-dynamic-keys
	const msg = i18n.t( msgKey );
	const msgParts = msg.split( /(\$\d+)/ );
	const placeholderRegex = /\$(\d+)/;
	return msgParts.map( ( elm ) => {
		const m = elm.match( placeholderRegex );
		if ( m !== null ) {
			const idx = parseInt( m[ 1 ], 10 ) - 1;
			return msgArgs[ idx ];
		}
		return elm;
	} );
}

/**
 * Render components to display a localized message including HTML.
 *
 * This is a replacement for vue-i18n's `i18n` element required by our use of
 * BananaFormatter as a replacement for vue-i18n's default renderer.
 *
 * Each child element in this tag's default slot is treated as a positional
 * argument for interpolation into the named message.
 *
 * @param {Function} h - Vue's createElement factory
 * @param {Object} ctx - Render context
 * @param {Object} ctx.props - An object of the provided props
 * @param {Function} ctx.slots - A function returning a slots object
 * @param {Object} ctx.data - The entire data object for the component
 * @return {Object} root component to render
 */
export function render( h, ctx ) {
	const props = ctx.props;
	const args = ctx.slots().default.filter( ( child ) => {
		return child.tag || child.test.trim() !== '';
	} );
	const children = buildNodes( props.msg, args );
	const tag = ( !!props.tag && props.tag !== true ) || props.tag === false ?
		props.tag :
		'span';
	return tag ? h( tag, ctx.data, children ) : children;
}

export default {
	name: 'I18nHtml',
	functional: true,
	props: {
		/**
		 * Message key to render.
		 */
		msg: {
			type: String,
			required: true
		},
		/**
		 * Tag to wrap output in.
		 *
		 * Leave as default `false` value to omit wrapper tag from output.
		 */
		tag: {
			type: [ String, Boolean, Object ],
			default: false
		}
	},
	render
};
