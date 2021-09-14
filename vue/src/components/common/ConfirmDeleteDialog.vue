<template>
	<v-container>
		<v-dialog
			v-model="show"
			persistent
			max-width="600px"
			@keydown.esc="show = false"
		>
			<v-card>
				<v-card-title>
					<span class="text-h5">{{ $t( 'confirmdelete-dialog-title' ) }}</span>
				</v-card-title>

				<v-card-text>
					<v-container>
						<v-row>
							{{ $t( 'confirmdelete-dialog-subtitle' ) }}
						</v-row>
					</v-container>
				</v-card-text>

				<v-card-actions>
					<v-spacer />
					<v-btn
						@click="show = false"
					>
						<v-icon
							class="me-2"
						>
							mdi-cancel
						</v-icon>
						{{ $t( 'cancel' ) }}
					</v-btn>

					<v-btn
						color="error base100--text"
						dark
						@click="confirmDelete"
					>
						<v-icon
							dark
							class="me-2"
						>
							mdi-delete
						</v-icon>
						{{ $t( 'delete' ) }}
					</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>
	</v-container>
</template>

<script>
export default {
	name: 'ConfirmDeleteDialog',
	props: {
		value: {
			type: Boolean,
			required: false
		}
	},
	computed: {
		show: {
			get() {
				return this.value;
			},
			set( value ) {
				this.$emit( 'input', value );
			}
		}
	},
	methods: {
		confirmDelete() {
			this.$emit( 'delete' );
		}
	}
};
</script>
