import i18n from '@/plugins/i18n';
import { mapGetters } from 'vuex';
import EventIcon from '@/components/auditlog/EventIcon';
import EventTimestamp from '@/components/auditlog/EventTimestamp';
import UserLink from '@/components/auditlog/UserLink';

/**
 * Generate a list of nodes to output based on message interpolation.
 *
 * This is a hacky way to get our Banana-i18n integration to work similar to
 * the <i18n> component from vue-i18n. The `$t()` function always treats
 * message arguments as plain text. This is actually a really good thing for
 * avoiding XSS and similar issues from untrusted input. It makes templating
 * complex things like an audit log message tricky however.
 *
 * This builder takes inspiration from <i18n> and emits an array of values to
 * be added to the DOM. These values can be plain strings or VNode objects
 * that Vue knows how to render as HTML. The list is computed by first getting
 * the localized message _without_ expanding its parameter placeholders. That
 * localized stirng is then split on the placeholders to produce something
 * like `['string', 'placeholder', 'string', 'placeholder', 'string']`. The
 * code then walks this array and for each element emits either the output of
 * `wrap('string')` or the provided argument matching the placeholder
 * position. This output is suitable for use as the children array for
 * a VNode.
 *
 * @param {Object} log - Log event being rendered
 * @param {Object[]} msgArgs - Arguments to interpolate into message
 * @param {Function} wrap - Function to generate wrapper elements for text
 * @param {boolean} rtl - Is the current locale RTL?
 * @return {Object[]} List of nodes to emit for rendering
 */
export function buildNodes( log, msgArgs, wrap, rtl ) {
	const action = log.action.replace( ' ', '-' );
	const msgKey = 'auditlog-entry-' + log.target.type + '-' + action;
	// eslint-disable-next-line @intlify/vue-i18n/no-dynamic-keys
	const msg = i18n.t( msgKey );
	const msgParts = msg.split( /(\$\d+)/ );
	if ( rtl ) {
		// Flip array when in an RTL locale so that our re-wrapping maintains
		// RTL order when rendered as HTML. Note that this would not be
		// necessary if we emitted the text nodes raw instead of wrapping them
		// in <dd> nodes.
		msgParts.reverse();
	}
	const placeholderRegex = /\$(\d+)/;
	const children = msgParts.map( ( elm ) => {
		const m = elm.match( placeholderRegex );
		if ( m !== null ) {
			const idx = parseInt( m[ 1 ], 10 ) - 1;
			return msgArgs[ idx ];
		} else if ( elm ) {
			return wrap( elm, { class: 'log-event-text' } );
		}
		return null;
	} );

	if ( log.message ) {
		children.push( wrap(
			[ '(', log.message, ')' ],
			{ class: 'log-event-message' }
		) );
	}
	return children;
}

/**
 * Render components to display a LogEvent.
 *
 * @param {Function} createElement - Vue's createElement factory
 * @return {Object} root component to render
 */
export function render( createElement ) {
	/**
	 * Emit a <router-link>.
	 *
	 * @param {Object} props - Component props
	 * @param {string} label - Link text
	 * @return {Object}
	 */
	const link = function ( props, label ) {
		return createElement( 'router-link', { props }, [ label ] );
	};

	/**
	 * Emit a node describing a user.
	 *
	 * @param {Object} user_ - User information
	 * @param {number} user_.id - User id
	 * @param {string} user_.username - User username
	 * @param {boolean} showTalk - Display link to user_'s Talk page
	 * @return {Object}
	 */
	const user = function ( user_, showTalk = false ) {
		// Be defensive unpacking user when dealing with legacy records in dev
		// and test environments.
		const id = user_ && user_.id || null;
		const username = user_ && user_.username || null;
		return createElement( 'UserLink',
			{ props: { user: { id, username }, showTalk } },
			[ username ]
		);
	};

	/**
	 * Emit a <dd> node.
	 *
	 * @param {Object[]} children - child nodes for the <dd>
	 * @param {?Object} parameters - extra parameters for node
	 * @return {Object}
	 */
	const dd = function ( children, parameters = {} ) {
		return createElement( 'dd', parameters, children );
	};

	const target = this.log.target;
	const params = this.log.params || {};
	const msgArgs = [ user( this.log.user, true ) ];

	if ( target.type === 'tool' ) {
		msgArgs.push( dd( [
			'"',
			link(
				{ to: { name: 'tools-view', params: { name: target.label } } },
				target.label
			),
			'"'
		], { class: 'log-event-tool' } ) );
	}
	if ( target.type === 'toollist' ) {
		msgArgs.push( dd( [
			'"',
			link(
				{ to: { name: 'lists-view', params: { id: target.id } } },
				target.label
			),
			'"'
		], { class: 'log-event-toollist' } ) );
	}
	if ( target.type === 'url' ) {
		msgArgs.push( dd( [
			'"',
			createElement( 'a',
				{ attrs: { href: target.label, target: '_blank' } },
				[ target.label ]
			),
			'"'
		], { class: 'log-event-url' } ) );
	}
	if ( target.type === 'user' ) {
		msgArgs.push( user( { id: target.id, username: target.label } ) );
	}
	if ( target.type === 'group' ) {
		msgArgs.push( user( params.user ) );
		msgArgs.push( dd( [
			'"',
			link(
				{ to: { name: 'members', query: { groups_id: target.id } } },
				[ target.label ]
			),
			'"'
		], { class: 'log-event-group' } ) );
	}
	if ( target.type === 'version' ) {
		msgArgs.push( dd( [
			link(
				{
					to: {
						name: 'tools-revision',
						params: {
							name: params.tool_name,
							revId: String( target.id )
						}
					}
				},
				[ target.id ]
			)
		], { class: 'log-event-version' } ) );
		msgArgs.push( dd( [
			'"',
			link(
				{ to: { name: 'tools-view', params: { name: params.tool_name } } },
				[ params.tool_name ]
			),
			'"'
		], { class: 'log-event-tool' } ) );
	}

	return createElement(
		'dl',
		{ class: 'log-event row elevation-2 ma-1 mb-2 pa-4' },
		[
			createElement( 'EventIcon', { props: { log: this.log } } ),
			createElement( 'EventTimestamp', { props: { log: this.log } } ),
			...buildNodes( this.log, msgArgs, dd, this.isRTL )
		]
	);
}

export default {
	name: 'LogEvent',
	components: {
		EventIcon,
		EventTimestamp,
		UserLink
	},
	props: {
		/**
		 * Log event to render.
		 */
		log: {
			type: Object,
			required: true
		}
	},
	computed: {
		...mapGetters( 'locale', [ 'isRTL' ] )
	},
	render
};
