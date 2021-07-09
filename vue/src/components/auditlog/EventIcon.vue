<template>
	<dd class="log-event-icon">
		<v-icon size="20">
			{{ eventIcon( log.action ) }}
		</v-icon>
	</dd>
</template>

<script>
export default {
	name: 'EventIcon',
	props: {
		/**
		 * Log event to render.
		 */
		log: {
			type: Object,
			required: true
		}
	},
	methods: {
		eventIcon( action ) {
			switch ( action ) {
				case 'created':
					return 'mdi-note-plus-outline';
				case 'updated':
					return 'mdi-update';
				case 'deleted':
					return 'mdi-delete-outline';
				case 'added to':
					return 'mdi-account-multiple-plus-outline';
				case 'removed from':
					return 'mdi-account-multiple-minus-outline';
				case 'hid':
					return 'mdi-eye-off-outline';
				case 'revealed':
					return 'mdi-eye-outline';
				case 'patrolled':
					return 'mdi-eye-check-outline';
				case 'featured':
					return 'mdi-star-plus-outline';
				case 'unfeatured':
					return 'mdi-star-remove-outline';
				default:
					return 'mdi-crosshairs-question';
			}
		}
	}
};
</script>
