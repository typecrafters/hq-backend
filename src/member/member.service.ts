import { Injectable, InternalServerErrorException, NotFoundException } from "@nestjs/common";
import { InjectRepository } from "@nestjs/typeorm";
import { Member } from "./member.entity";
import { MongoRepository } from "typeorm";
import { CreateMemberRequest } from "./dto/create-member-request.dto";
import { UpdateMemberRequest } from "./dto/update-member-request.dto";
import { ObjectId } from "mongodb";
import { FileService } from "@/file/file.service";

@Injectable()
export class MemberService {
    constructor(
        @InjectRepository(Member) private readonly memberRepository: MongoRepository<Member>,
        private readonly fileService: FileService
    ) { }

    public async list(page: number, limit: number): Promise<Array<Member>> {
        const maxLimit = 24;
        const clamp = Math.min(limit, maxLimit);
        try {
            const members = await this.memberRepository.find({
                skip: clamp * (page - 1),
                take: clamp,
                order: { createdAt: -1 }
            });

            return await Promise.all(members.map(async m => {
                m.profilePictureUrl = await this.fileService.getSignedUrl(m.profilePictureUrl);
                return m;
            }));
        } catch {
            throw new InternalServerErrorException("Failed to fetch member list.");
        }
    }

    public async get(id: string): Promise<Member> {
        const notFound = new NotFoundException("Member '" + id + "' not found.");
        if (!ObjectId.isValid(id)) throw notFound;

        const member = await this.memberRepository.findOneBy({ _id: new ObjectId(id) });
        if (member == null) throw notFound;

        member.profilePictureUrl = await this.fileService.getSignedUrl(member.profilePictureUrl);
        return member;
    }

    public async create(request: CreateMemberRequest): Promise<Member> {
        const member: Member = this.memberRepository.create({
            ...request,
            bio: request.bio ?? "",
            profilePictureUrl: request.profilePictureUrl ?? this.fileService.placeholder
        });

        return await this.memberRepository.save(member);
    }

    public async update(id: string, request: UpdateMemberRequest): Promise<void> {
        const notFound = new NotFoundException("Member '" + id + "' not found.");
        if (!ObjectId.isValid(id)) throw notFound;

        const patch = Object.fromEntries(
            Object.entries(request).filter(([_, v]) => v != null)
        );

        if (Object.keys(patch).length === 0) return;

        try {
            const result = await this.memberRepository.updateOne(
                { _id: new ObjectId(id) },
                { $set: patch }
            );

            if (result.matchedCount === 0) throw notFound;
        } catch {
            throw new InternalServerErrorException("Failed to update member.");
        }
    }

    public async delete(id: string): Promise<void> {
        const notFound = new NotFoundException("Member '" + id + "' not found.");
        if (!ObjectId.isValid(id)) throw notFound;

        try {
            const result = await this.memberRepository.deleteOne({ _id: new ObjectId(id) });

            if (result.deletedCount === 0) throw notFound;
        } catch {
            throw new InternalServerErrorException("Failed to delete member.");
        }
    }
} 