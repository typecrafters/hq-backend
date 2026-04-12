import { BadRequestException, Injectable, InternalServerErrorException, NotFoundException } from "@nestjs/common";
import { InjectRepository } from "@nestjs/typeorm";
import { MongoRepository } from "typeorm";
import { User } from "./user.entity";
import { ObjectId } from "mongodb";
import { UserStatus } from "./dto/user-status.enum";
import { ColorScheme } from "./dto/color-scheme.enum";
import { FileService } from "@/file/file.service";
import { MailService } from "@/mail/mail.service";
import { VerificationTokenService } from "@/verification-token/verification-token.service";
import { ConfigService } from "@nestjs/config";

@Injectable()
export class UserService {
    constructor(
        @InjectRepository(User) private readonly userRepository: MongoRepository<User>,
        private readonly fileService: FileService,
        private readonly mailService: MailService,
        private readonly tokenService: VerificationTokenService,
        private readonly config: ConfigService
    ) { }

    public async list(page: number, limit: number): Promise<Array<User>> {
        const maxLimit = 24;
        const clamp = Math.min(limit, maxLimit);

        try {
            const users =  await this.userRepository.find({
                skip: clamp * (page - 1),
                take: clamp,
                order: { createdAt: -1 }
            }); 

            return await Promise.all(users.map(async u => {
                u.profilePictureUrl = await this.fileService.getSignedUrl(u.profilePictureUrl);
                return u;
            }));
        } catch {
            throw new InternalServerErrorException("Failed to fetch project list.");
        }
    }

    public async existsByEmail(email: string): Promise<boolean> {
        const result = await this.userRepository.findOneBy({ email });
        return result !== null;
    }

    public async create(firstName: string, lastName: string, email: string, permissions: string[]) {
        if (await this.existsByEmail(email))
            throw new BadRequestException("User with this email already exists.");
        
        const user = this.userRepository.create({
            firstName,
            lastName,
            email,
            password: "",
            profilePictureUrl: this.fileService.placeholder,
            status: UserStatus.Unverified,
            preferredTheme: ColorScheme.System,
            permissions: [...new Set(permissions)]
        });

        const result = await this.userRepository.save(user);
        const token = await this.tokenService.createForEmail(result.id.toString());        
        
        const url = new URL("/email/verify", this.config.getOrThrow("PAGE_URL"));
        url.searchParams.set("sub", result.id.toString());
        url.searchParams.set("token", token);

        await this.mailService.renderAndSend(email, "Confirm your email addresss", "verify-email.ejs", {
            firstName: result.firstName,
            url: url.toString()
        });
    }

    public async getById(id: string): Promise<User> {
        const user = await this.userRepository.findOneBy({ id: new ObjectId(id) });

        if (user === null) throw new NotFoundException("User not found.");

        user.profilePictureUrl = await this.fileService.getSignedUrl(user?.profilePictureUrl);
        return user;
    }

    public async getByEmail(email: string): Promise<User | null> {
        const user = await this.userRepository.findOneBy({ email });

        if (user === null) throw new NotFoundException("User not found.");

        user.profilePictureUrl = await this.fileService.getSignedUrl(user?.profilePictureUrl);
        return user;
    }

    public async update(id: string, user: Partial<User>): Promise<void> {
        const notFound = new NotFoundException("Project '" + id + "' not found.");
        if (!ObjectId.isValid(id)) throw notFound;

        const patch = Object.fromEntries(
            Object.entries(user).filter(([_, v]) => v != null)
        );

        if (Object.keys(patch).length === 0) return;

        try {
            const result = await this.userRepository.updateOne(
                { _id: new ObjectId(id) },
                { $set: patch }
            );

            if (result.matchedCount === 0) throw notFound;
        } catch {
            throw new InternalServerErrorException("Failed to update project.");
        }
    }

    public async updatePasswordById(id: string, passwordHash: string): Promise<void> {
        await this.update(id, { password: passwordHash });
    }

    public async activateById(id: string) {
        return this.update(id, { status: UserStatus.Active });
    }
}