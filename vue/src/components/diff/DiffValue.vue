<template>
	<v-row v-if="value !== null"
		class="cols diff-value"
	>
		<v-col cols="1">
			<v-icon
				class="mt-3"
				color="base20"
				small
			>
				{{ icon }}
			</v-icon>
		</v-col>

		<v-col cols="11" class="ps-0">
			<v-alert
				colored-border
				dense
				border="left"
				:color="borderColor"
				elevation="2"
			>
				{{ value }}
			</v-alert>
		</v-col>
	</v-row>
</template>

<script>
const ADD = 'add';
const REMOVE = 'remove';

export default {
	name: 'DiffValue',
	props: {
		op: {
			required: true,
			validator: function ( value ) {
				return [ ADD, REMOVE ].indexOf( value ) !== -1;
			}
		},
		// eslint-disable-next-line vue/require-prop-types
		value: {
			required: false,
			default: null
		}
	},
	computed: {
		borderColor() {
			return ( this.op === ADD ? 'green' : 'red' ) + ' lighten-1';
		},
		icon() {
			return this.op === ADD ? 'mdi-plus' : 'mdi-minus';
		}
	}
};
</script>
