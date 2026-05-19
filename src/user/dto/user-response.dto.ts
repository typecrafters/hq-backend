import { UserStatus } from "./user-status.enum";
import { User } from "../user.schema";

export class UserResponse {
	public id!: string;
	public firstName!: string;
	public lastName!: string;
	public email!: string;
	public role!: string;
	public profilePictureUrl!: string;
	public status!: UserStatus;

	private constructor(partial: Partial<UserResponse>) {
		Object.assign(this, partial);
	}

	public static fromUser(user: User): UserResponse {
		return new UserResponse({
			id: user._id.toString(),
			firstName: user.firstName,
			lastName: user.lastName,
			email: user.email,
			role: user.role,
			profilePictureUrl: user.profilePictureUrl,
			status: user.status,
		});
	}
}

