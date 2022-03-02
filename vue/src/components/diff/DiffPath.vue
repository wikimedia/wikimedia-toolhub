<template>
	<dl class="row diff-path">
		<template v-for="( value, idx ) in path">
			<dt
				:key="idx"
				class="me-1"
			>
				{{ labelFor( value ) }}
			</dt>
			<!-- eslint-disable-next-line vue/require-v-for-key -->
			<dt v-if="idx !== path.length - 1"
				class="me-1"
			>
				/
			</dt>
		</template>
	</dl>
</template>

<script>
export default {
	name: 'DiffPath',
	props: {
		path: {
			type: Array,
			required: true
		}
	},
	methods: {
		/**
		 * Compute a localized label for a property.
		 *
		 * @param {string|number} prop - Property (e.g. 'tool_type')
		 * @return {string} Localized label for property
		 */
		labelFor( prop ) {
			if ( typeof prop === 'string' ) {
				const key = prop.replace( /_/g, '' );
				// eslint-disable-next-line @intlify/vue-i18n/no-dynamic-keys
				return this.$i18n.t( key );
			}
			return prop.toString();
		}
	}
};
</script>
